from copy import deepcopy
import math
from datetime import date

MODEL_VERSION = '2.0.0'

WEIGHTS = {'NC formali': 30, 'Criticità informali': 8, 'Attività': 22,
           'Interferenze': 15, 'Organizzazione': 10, 'Presidio e controlli': 15}

THEMES = ['elettrico', 'scavi', 'quota', 'sollevamento', 'spazi confinati',
          'incendio', 'viabilità', 'dpi', 'ordine e pulizia', 'documentale', 'ambientale', 'altro']

THEME_FACTOR = dict(zip(THEMES, [1.2, 1.2, 1.15, 1.15, 1.25, 1.15, 1.05, .85, .7, .65, 1., .85]))

SEVERITY = {'bassa': 1., 'media': 2.5, 'alta': 5.}

STATUS = {'Aperta': 1., 'Chiusa nei tempi': .2, 'Chiusa in ritardo': .4}

ACTIVITY = {'elettrici': 80, 'scavi': 75, 'lavori in quota': 85, 'sollevamenti': 80,
            'spazi confinati': 95, 'hot work': 75, 'movimentazione mezzi': 55,
            'civili': 35, 'meccanici': 45, 'altro': 40}

ACTIVITY_THEME = {'elettrici': 'elettrico', 'scavi': 'scavi', 'lavori in quota': 'quota',
                  'sollevamenti': 'sollevamento', 'spazi confinati': 'spazi confinati',
                  'hot work': 'incendio', 'movimentazione mezzi': 'viabilità',
                  'civili': 'ordine e pulizia', 'meccanici': 'dpi', 'altro': 'altro'}

PHASE_THEMES = {'cantierizzazione': ['scavi', 'viabilità', 'ordine e pulizia'],
                'costruzione': ['quota', 'sollevamento', 'dpi'],
                'commissioning': ['elettrico', 'incendio', 'dpi'],
                'punch list': ['elettrico', 'quota', 'ordine e pulizia']}

def bounded(x, low=0., high=100.):
    return max(low, min(high, float(x)))

def risk_level(x):
    return ['Basso', 'Medio basso', 'Medio', 'Alto', 'Critico'][min(4, max(0, math.ceil(x / 20) - 1))]

def default_data():
    today = date.today().replace(day=1)
    last_month = date(today.year - (today.month == 1), 12 if today.month == 1 else today.month - 1, 1)
    return dict(nome='', technology='Wind', fase='costruzione', month=last_month.isoformat()[:7],
                app=1, sub=0, company_hse=1, hse_coverage=80., inspections=0,
                inspection_target=4, activities=['civili'], interference_level=3,
                nc_items=[], crit_items=[], awareness=[], stop_positive=0, stop_negative=0,
                imminent_danger=False, hours=None, workers=None, days=None, notes='')

def anomaly_load(rows):
    return sum(SEVERITY[r['severity']] * THEME_FACTOR[r['theme']] * STATUS[r['status']]
               * (1.25 if r['late'] else 1) * (1.2 if r['repeat'] else 1) for r in rows)

def topic_needs(d):
    needs, reasons = {}, {}
    for activity in d['activities']:
        theme = ACTIVITY_THEME[activity]
        needs[theme] = max(needs.get(theme, 0), ACTIVITY[activity] / 100)
        reasons.setdefault(theme, []).append('attività: ' + activity)
    for field, label, factor in [('nc_items', 'NC formale', 1.), ('crit_items', 'criticità informale', .5)]:
        for row in d[field]:
            if row['status'] == 'Aperta':
                theme = row['theme']
                needs[theme] = needs.get(theme, 0) + SEVERITY[row['severity']] / 5 * factor
                reasons.setdefault(theme, []).append(f"{label} aperta, gravità {row['severity']}")
    for theme in PHASE_THEMES[d['fase']]:
        needs[theme] = max(needs.get(theme, 0), .2)
        reasons.setdefault(theme, []).append('coerenza con fase ' + d['fase'])
    return needs, reasons

def calculate_risk(d):
    """Pesi ipotetici di policy, versionati. Nessuna stima statistica degli infortuni.
    Indice base sempre confrontabile; contesto opzionale separato.
    """
    nc_load, crit_load = anomaly_load(d['nc_items']), anomaly_load(d['crit_items'])
    nc = 100 * (1 - math.exp(-nc_load / 10))
    crit = 100 * (1 - math.exp(-crit_load / 12))
    activity = min(100, max(ACTIVITY[a] for a in d['activities']) + 3 * (len(d['activities']) - 1))
    interference = (d['interference_level'] - 1) / 9 * 100
    org = 100 * (1 - math.exp(-(max(0, d['app'] - 1) + 1.2 * d['sub']) / 8))
    # Nessun requisito universale "un HSE per impresa": si valuta la copertura reale dichiarata.
    inspection_deficit = 100 * (1 - min(1, d['inspections'] / d['inspection_target']))
    controls = .65 * (100 - d['hse_coverage']) + .35 * inspection_deficit
    components = dict(zip(WEIGHTS, [nc, crit, activity, interference, org, controls]))
    drivers = [{'Area': key, 'Indice area': round(value, 3), 'Peso massimo': WEIGHTS[key],
                'Contributo': value * WEIGHTS[key] / 100} for key, value in components.items()]
    positive = min(2., d['stop_positive'] * .5)
    negative = min(6., d['stop_negative'] * 1.5)
    needs, reasons = topic_needs(d)
    numerator = 0.
    awareness_details = []
    for row in d['awareness']:
        theme = row['theme']
        coverage = row['coverage'] / 100 if row['coverage'] is not None else .5
        continuity = min(1., .7 + .1 * (row['count'] - 1))
        effectiveness = coverage * continuity
        contribution = needs.get(theme, 0) * effectiveness
        numerator += contribution
        awareness_details.append({'Tema': theme, 'Incontri': row['count'],
            'Copertura': f"{row['coverage']:.0f}%" if row['coverage'] is not None else 'Non nota: fattore 50%',
            'Pertinenza': round(needs.get(theme, 0), 3), 'Efficacia convenzionale': round(effectiveness, 3),
            'Motivo': '; '.join(reasons.get(theme, ['Nessun collegamento agli input: nessun bonus']))})
    awareness = 8 * numerator / sum(needs.values()) if needs else 0.
    raw = sum(x['Contributo'] for x in drivers) + negative - positive - awareness
    high_open = sum(r['severity'] == 'alta' and r['status'] == 'Aperta' for r in d['nc_items'])
    floor = 81. if d['imminent_danger'] or high_open >= 2 else 61. if high_open == 1 else 0.
    floor_reason = ('Pericolo grave e attuale dichiarato' if d['imminent_danger'] else
                    'Almeno due NC formali alte aperte' if high_open >= 2 else
                    'Una NC formale alta aperta' if high_open else 'Nessuna soglia minima attiva')
    score = max(floor, bounded(raw))
    # Esposizione solo nell'indice contestualizzato: ore > giorni > lavoratori.
    contextual_target, context_basis = None, 'Nessun dato di esposizione disponibile'
    if d.get('hours'):
        contextual_target, context_basis = max(1., d['hours'] / 2000), '1 ispezione ogni 2.000 ore lavorate'
    elif d.get('days'):
        contextual_target = max(1., d['days'] / 5 * max(1., (d.get('workers') or 50) / 50))
        context_basis = '1 ispezione ogni 5 giorni operativi e ogni 50 lavoratori medi (minimo fattore 1)'
    elif d.get('workers'):
        contextual_target, context_basis = max(1., 4 * d['workers'] / 50), '4 ispezioni per 50 lavoratori medi nel mese'
    contextual = None
    if contextual_target:
        context_controls = .65 * (100 - d['hse_coverage']) + .35 * 100 * (1 - min(1., d['inspections'] / contextual_target))
        contextual = max(floor, bounded(raw + (context_controls - controls) * .15))
    saturation = bounded(raw) - raw
    drivers.extend([{'Area': 'Stop Work negativi', 'Indice area': None, 'Peso massimo': 6, 'Contributo': negative},
                    {'Area': 'Stop Work positivi', 'Indice area': None, 'Peso massimo': -2, 'Contributo': -positive},
                    {'Area': 'Sensibilizzazioni pertinenti', 'Indice area': None, 'Peso massimo': -8, 'Contributo': -awareness},
                    {'Area': 'Limite scala 0–100', 'Indice area': None, 'Peso massimo': None, 'Contributo': saturation},
                    {'Area': 'Soglia minima di tutela', 'Indice area': None, 'Peso massimo': None, 'Contributo': score - bounded(raw)}])
    explanations = [
        f'NC formali: carico {nc_load:.2f}; indice area = 100 × (1 − exp(−carico/10)); massimo 30 punti.',
        f'Criticità informali: carico {crit_load:.2f}; indice area = 100 × (1 − exp(−carico/12)); massimo 8 punti.',
        'Carico anomalia = gravità (1/2,5/5) × tema (0,65–1,25) × stato (aperta 1; chiusa nei tempi 0,2; chiusa in ritardo 0,4) × scaduta (1,25) × recidiva (1,2).',
        'I temi modificano la priorità convenzionale; la gravità deve essere assegnata in base al potenziale danno del caso concreto.',
        'Attività: massima pericolosità convenzionale + 3 per ogni tipologia aggiuntiva, massimo 100; peso 22%.',
        'Interferenze: (livello − 1)/9 × 100, peso 15%. Non viene riapplicata la pericolosità delle attività.',
        'Organizzazione: 100 × (1 − exp(−(appaltatori−1 + 1,2×subappaltatori)/8)), peso 10%.',
        f'Presidio: 65% deficit copertura HSE + 35% deficit ispezioni rispetto al target dichiarato ({d["inspection_target"]}); peso 15%.',
        'Nessun malus sul rapporto NC/ispezioni: rilevare più anomalie non rende meno efficace il controllo. Il rapporto resta descrittivo.',
        f'Sensibilizzazioni: −{awareness:.2f}/8. Copertura ponderata dei temi necessari; continuità da 0,7 a 1; copertura non nota usa fattore prudenziale 0,5.',
        f'Stop Work: positivi −{positive:.2f}/2; negativi +{negative:.2f}/6. Ogni evento va classificato una sola volta; anomalia sottostante registrata una sola volta.',
        f'Soglia minima: {floor:.0f}. {floor_reason}. Le criticità informali da sole non attivano una soglia.',
        'I pesi più alti delle NC formali sono una scelta gestionale richiesta, non una dimostrazione di maggiore pericolosità fisica.',
        'Pesi, soglie e target sono ipotesi iniziali di calibrazione; non derivano da dati storici né da un modello predittivo validato.'
    ]
    missing = []
    if not d['inspections']:
        missing.append('Nessuna ispezione: assenza di NC non dimostra assenza di anomalie.')
    if any(d.get(k) is None for k in ['hours', 'workers', 'days']):
        missing.append('Dati di esposizione parziali o assenti: usare l’indice base per la graduatoria comune.')
    if any(r['coverage'] is None for r in d['awareness']):
        missing.append('Copertura delle sensibilizzazioni non sempre nota.')
    return dict(version=MODEL_VERSION, score=round(score, 2), level=risk_level(score),
                raw=round(raw, 3), floor=floor, floor_reason=floor_reason,
                drivers=drivers, awareness_details=awareness_details, awareness_bonus=round(awareness, 3),
                needs=needs, reasons=reasons, context_score=round(contextual, 2) if contextual is not None else None,
                context_target=round(contextual_target, 2) if contextual_target else None, context_basis=context_basis,
                explanations=explanations, missing=missing)

def simulations(d, r):
    """Ricalcolo del medesimo modello: non previsione della riduzione reale del rischio."""
    rows = []
    changes = [
      ('Chiusura verificata delle NC aperte', lambda x: [item.update(status='Chiusa nei tempi', late=False) for item in x['nc_items'] if item['status'] == 'Aperta']),
      ('Chiusura verificata delle criticità aperte', lambda x: [item.update(status='Chiusa nei tempi', late=False) for item in x['crit_items'] if item['status'] == 'Aperta']),
      ('Copertura HSE al 100%', lambda x: x.update(hse_coverage=100)),
      ('Target ispettivo raggiunto', lambda x: x.update(inspections=max(x['inspections'], x['inspection_target']))),
      ('Interferenza ridotta di 2 livelli', lambda x: x.update(interference_level=max(1, x['interference_level'] - 2))),
      ('Toolbox pertinenti: 4 incontri per tema, copertura 100%', lambda x: x.update(awareness=[{'theme': t, 'count': 4, 'coverage': 100.} for t in topic_needs(x)[0]]))]
    for label, apply in changes:
        sample = deepcopy(d)
        apply(sample)
        result = calculate_risk(sample)
        rows.append({'Scenario indipendente': label, 'Indice simulato': result['score'],
                     'Riduzione punti': round(r['score'] - result['score'], 2),
                     'Soglia residua': result['floor']})
    return rows
