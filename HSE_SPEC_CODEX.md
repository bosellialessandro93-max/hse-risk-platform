# HSE Risk Platform — Specifica Codex

Versione 1.2 · 19 ottobre 2026

Copia testuale completa del documento Word. Gli ID RF/AT sono i riferimenti per implementazione e test. La figura illustrativa della pagina risultati è descritta dai requisiti e non contiene nuovi dati di calcolo.

SPECIFICA DI PRODOTTO / 01

## HSE Risk Index
Requisito completo

Specifica funzionale, esperienza utente e interfaccia grafica
Versione requisito 1.2 • 19 ottobre 2026

### Obiettivo

Realizzare un ambiente unico per valutare mensilmente i cantieri Wind, Solar e BESS, spiegare i fattori che determinano l’indice, individuare le priorità operative e consultare la pianificazione condivisa delle imprese. Ogni risultato deve essere leggibile, riproducibile e collegato ai dati che lo hanno generato.

### Ordine di prevalenza

Le richieste più recenti dell’utente prevalgono sulle schermate e sulle descrizioni precedenti. Il riferimento funzionale aggiornato è la guida del 16 ottobre 2026, interfaccia 3.1.0 e modello 2.0.0. La metodologia iniziale di luglio appartiene a una versione precedente e non deve essere sommata o sovrapposta al modello aggiornato.

### Stato dei requisiti

| Codice | Significato |
| --- | --- |
| C | Consolidato: comportamento documentato o richiesta esplicita dell’utente. |
| P | Proposta: miglioramento funzionale o UX/UI da introdurre. |
| V | Verifica tecnica: dettaglio da ricavare dal motore di calcolo aggiornato prima del rilascio. |

### Perimetro

Comprende valutazione mensile, risultati e azioni, NC e criticità, sensibilizzazioni, storico e revisioni, confronto cantieri, sinottici impresa, calendario condiviso, toolkit ed esportazioni. Il documento definisce il prodotto e i criteri di accettazione; non costituisce una nuova implementazione del tool.

### Risultato atteso per l’utilizzatore

Capire dove intervenire, perché e con quale priorità; compilare solo le informazioni utili; distinguere in ogni momento bozza, calcolo e salvataggio. L’indice resta un indicatore gestionale sperimentale, distinto dalla probabilità di infortunio e dalle valutazioni di sicurezza applicabili.

SPECIFICA DI PRODOTTO / 02

## Navigazione e percorsi utente

### RF-01 · Accesso e ruoli [C / P]

Conservare i percorsi HSE Enel e HSE impresa. Enel accede a valutazioni, risultati, storico, confronti e calendario; impresa a pianificazione, sinottici e revisioni. Attualmente la scelta del percorso con password condivisa non costituisce separazione delle autorizzazioni. Proposta: account nominativi e permessi per cantiere prima di qualificare il sistema come gestione dei ruoli.

### RF-02 · Struttura principale [P]

| Voce | Contenuto principale |
| --- | --- |
| Panoramica | Ultime valutazioni salvate, stato dati, accesso rapido ai cantieri. |
| Valutazione mensile | Compilazione guidata e verifica dei dati. |
| Risultati e azioni | Sintesi, contributi, alert, registro e Action Plan. |
| Storico cantiere | Trend mensile e revisioni. |
| Confronto cantieri | Graduatoria con criteri omogenei. |
| Calendario condiviso | Programmazione pubblicata dalle imprese. |
| Archivio e impostazioni | Backup e politiche comuni del modello. |

### RF-03 · Valutazione guidata [C / P]

Proporre quattro passaggi: 1. Cantiere e attività; 2. Segnalazioni; 3. Presidio e prevenzione; 4. Verifica e calcolo. Mostrare avanzamento e sezioni incomplete. Consentire il ritorno ai passaggi precedenti senza perdere dati. Usare un riepilogo prima del calcolo, con errori collegati ai campi da correggere.

### RF-04 · Stati della valutazione [C / P]

Distinguere Bozza, Calcolata, Modificata dopo il calcolo e Salvata. Se un input cambia, il risultato precedente rimane identificato come non aggiornato e non può essere salvato come se rappresentasse i nuovi dati. Il pulsante Ricalcola deve essere evidente. Export e salvataggio devono riferirsi allo stesso insieme di input calcolati.

### RF-05 · Continuità [P]

Mantenere cantiere e mese visibili nell’intestazione. Mostrare le modifiche non salvate prima di lasciare il modulo. Le conferme devono essere brevi e specifiche; non chiedere conferme ripetute per operazioni ordinarie e reversibili.

SPECIFICA DI PRODOTTO / 03

## Dati del cantiere e validazioni

| ID / dato | Requisito |
| --- | --- |
| RF-06 · Identità [C/P] | Nome obbligatorio, massimo 120 caratteri; tecnologia Wind/Solar/BESS; mese e fase obbligatori. Proposta: ID stabile del cantiere e scelta da anagrafica per evitare duplicati. |
| RF-07 · Periodo [C] | Periodo mensile; nessun mese futuro. Il mese corrente è parziale ed escluso dalla graduatoria consolidata. Mostrare mese/anno anziché un giorno che viene ignorato. |
| RF-08 · Attività [C/P] | Almeno una lavorazione. Selezione multipla con etichette, stato selezionato riconoscibile e raggruppamento per tema. Conservare il catalogo del modello aggiornato. |
| RF-09 · Interferenze [C] | Scala 1–10: 1 separate; 3 contatti occasionali gestiti; 5 aree o risorse condivise; 7 sovrapposizioni frequenti; 10 interferenze continue senza separazione efficace. |
| RF-10 · Imprese [C] | Numero appaltatrici e subappaltatrici intero non negativo; somma almeno 1. Numero professionisti HSE descrittivo, senza impatto diretto. |
| RF-11 · Copertura HSE [C] | Percentuale 0–100 delle lavorazioni, turni e aree effettivamente coperte; distinta dal numero di professionisti HSE. |
| RF-12 · Esposizione [C/P] | Ore, lavoratori medi e giorni operativi facoltativi; giorni entro il mese. Nell’interfaccia nuova distinguere dato assente da zero reale. Conservare la compatibilità con gli zeri storici intesi come non disponibili. |
| RF-13 · Note [C] | Campo facoltativo per fonti, assunzioni e motivazioni. Nessuna trasformazione automatica del testo in un evento conteggiato. |

### Comportamento dei campi [P]

Indicare chiaramente obbligatorietà e unità di misura. Conteggi solo interi non negativi; ore non negative; percentuali entro i limiti. Non trattare i valori precompilati come dati verificati. Mostrare errori accanto al campo e un riepilogo in alto senza cancellare la compilazione.

### Qualità del dato [P]

Distinguere completezza, dato dichiarato e dato supportato da riferimento. Non assegnare un livello di rischio basso per la sola assenza di dati. Le informazioni facoltative mancanti non bloccano l’indice base; devono chiarire perché l’indice contestualizzato non è disponibile.

SPECIFICA DI PRODOTTO / 04

## NC formali e criticità informali

### RF-14 · Etichette e aiuti richiesti [C]

Eliminare “massimo 30 punti”, “massimo 8 punti” e qualsiasi analoga dicitura nei titoli di compilazione. Collocare un pulsante con punto interrogativo a destra di ciascun titolo, coerente con gli altri aiuti del tool.

| Sezione | Testo dell’aiuto |
| --- | --- |
| NC formali | Inserire solo le non conformità registrate in HSEQ4ALL e riferite al periodo preso in analisi. Non duplicare le segnalazioni già presenti tra le criticità informali. |
| Criticità informali | Inserire solo le non conformità non registrate in HSEQ4ALL e riferite al periodo preso in analisi. Non duplicare le segnalazioni già presenti tra le NC formali. |

### RF-15 · Scheda evento [C / P]

Ogni scheda deve contenere tema, gravità bassa/media/alta, stato a fine periodo (Aperta, Chiusa nei tempi, Chiusa in ritardo), opzioni “Aperta e oltre la scadenza” e “Segnalazione ricorrente”, descrizione e riferimento. Tema, gravità e stato sono obbligatori per ogni scheda creata. “Oltre la scadenza” è applicabile soltanto a eventi aperti. Proposta: richiedere una motivazione per gravità alta e consentire riferimento HSEQ4ALL per le formali.

### RF-16 · Periodo e unicità [C / P]

Per periodo preso in analisi si intendono gli eventi rilevati nel mese e quelli dei mesi precedenti ancora aperti a fine mese. Non riproporre chiusure già considerate. Se una criticità viene formalizzata, trasferirla al canale formale evitando il doppio conteggio; proposta: mantenere il collegamento alla registrazione originaria. Gli eventi chiusi restano nel registro e non generano nuove azioni di chiusura.

### RF-17 · Pericolo grave e attuale [C]

Conservare il campo “È ancora presente un pericolo grave e attuale a fine valutazione” con aiuto a destra: “Selezionare solo quando il pericolo è ancora presente a fine periodo. La condizione attiva un indice minimo di 81/100, indipendentemente dal canale di registrazione.” Un evento già risolto non giustifica il flag.

### Interazione [P]

Schede richiudibili con titolo descrittivo, gravità e stato visibili anche da chiuse. Pulsanti Aggiungi e Rimuovi locali alla sezione. Stato vuoto: “Nessuna segnalazione inserita per il periodo selezionato”. Una scheda incompleta impedisce il calcolo e viene aperta automaticamente.

SPECIFICA DI PRODOTTO / 05

## Ispezioni, Stop Work e prevenzione

### RF-18 · Ispezioni [C / P / V]

Nel modulo mostrare una sola domanda: “Numero ispezioni registrate in HSEQ4ALL”. Conteggio intero non negativo riferito al periodo analizzato. Eliminare la domanda visibile sul target mensile; il target resta un parametro comune configurato nelle impostazioni metodologiche, versionato e indicato nel dettaglio del risultato. Questa collocazione è una proposta attuativa per rispettare la richiesta di una sola domanda senza perdere confrontabilità.

Il punto interrogativo deve spiegare il calcolo della detection nel modello corrente: formula, popolazione di NC considerata, trattamento di zero ispezioni ed effetto sul punteggio. Per zero ispezioni evitare divisioni per zero e indicatori artificialmente favorevoli. L’espressione numerica esatta deve essere ricavata dal motore 2.0.0: non reintrodurre automaticamente la formula e i malus del modello di luglio.

### RF-19 · Stop Work [C / V]

Mostrare solo “Stop Work positivi” e “Stop Work negativi”, senza massimali o punteggi nelle etichette. Aiuto a destra: “Positivo: interruzione preventiva tempestiva e gestita; riduce l’indice fino a 2 punti. Negativo: stop imposto per carenze o mancato rispetto delle misure; aumenta l’indice fino a 6 punti. Classificare ogni Stop Work in una sola categoria e registrare una sola volta l’anomalia sottostante.”

I conteggi sono interi non negativi. Nel dettaglio del calcolo mostrare contributo effettivo, limite e regola per evento. Il valore unitario e la curva di saturazione devono coincidere con il motore aggiornato; i soli massimali non consentono di ricostruirli.

### RF-20 · Sensibilizzazioni [C]

Una scheda per argomento, con numero incontri effettivamente svolti nel mese almeno 1. Copertura dei destinatari unici facoltativa; senza dato noto il modello assume convenzionalmente il 50%, da rendere visibile. Bonus solo se pertinente rispetto ad attività, anomalie aperte e fase; massimo complessivo 8 punti. Eventi soltanto pianificati e download di toolbox non producono bonus.

### Microtesti [P]

Aiuti brevi nel modulo, approfondimenti nel dettaglio del calcolo. Un punto interrogativo deve funzionare con clic, tocco e tastiera, oltre al passaggio del mouse; contenuto persistente finché l’utente non lo chiude, senza coprire il campo attivo.

SPECIFICA DI PRODOTTO / 06

## Modello, soglie e tracciabilità

### RF-21 · Struttura del modello aggiornato [C]

| Componente | Contributo massimo |
| --- | --- |
| NC formali | 30 punti |
| Criticità informali | 8 punti |
| Attività | 22 punti |
| Interferenze | 15 punti |
| Organizzazione | 10 punti |
| Presidio e controlli | 15 punti |

I sei massimali sommano a 100. Applicare poi Stop Work negativi fino a +6, positivi fino a −2 e sensibilizzazioni pertinenti fino a −8. Il risultato deve restare tra 0 e 100. NC e criticità passano attraverso una funzione non lineare: numero di eventi e punti non sono equivalenti.

### RF-22 · Vincoli non compensabili [C]

Una NC formale alta aperta impone almeno 61/100; almeno due impongono almeno 81/100. Pericolo grave e attuale presente: almeno 81/100. Le sole criticità informali non attivano automaticamente tali soglie. I bonus non possono abbassare il risultato sotto la soglia attiva. Esporre il valore prima della soglia e l’adeguamento applicato, senza confonderlo con il contributo delle NC.

Fasce: 0–20 Basso; oltre 20 fino a 40 Medio basso; oltre 40 fino a 60 Medio; oltre 60 fino a 80 Alto; oltre 80 fino a 100 Critico. La classificazione usa il valore non arrotondato; l’interfaccia mostra un decimale, evitando incoerenze al confine delle fasce.

### RF-23 · Indice contestualizzato [C / V]

Separato dall’indice base e facoltativo: modifica soltanto il deficit ispettivo usando prima le ore; in loro assenza i giorni e, se disponibili, i lavoratori; senza ore e giorni usa i soli lavoratori. Mostrare fonte del target, assunzioni e risultato distinto. I target sono ipotesi gestionali. Non modificare le altre componenti tramite questi dati.

### RF-24 · Contratto tecnico del calcolo [P / V]

Prima del rilascio documentare funzioni non lineari, coefficienti, cataloghi, detection, target, saturazioni, gestione della fase, copertura HSE e pertinenza dei toolbox. Ogni calcolo deve registrare versione modello e politica, input, contributi grezzi/effettivi, bonus, soglie e risultato. I grafici devono riconciliare questi elementi con l’indice finale; nessun algoritmo va sostituito con valori dedotti dai soli massimali.

SPECIFICA DI PRODOTTO / 07

## Risultati: gerarchia visiva e azioni

### RF-25 · Prima schermata [P]

Aprire direttamente una sintesi decisionale: cantiere e mese, stato del salvataggio, indice base con fascia testuale, eventuale soglia minima attiva, segnalazioni aperte per gravità, tre contributi principali e azioni prioritarie. Indice contestualizzato e qualità dei dati devono essere riconoscibili e distinti dall’indice base.

Schema di impaginazione proposto. I numeri sono esclusivamente illustrativi e non rappresentano un risultato del modello.

### RF-26 · Grafici [P]

Usare barre orizzontali ordinate per contributo effettivo e un dettaglio a cascata per riconciliare componenti, bonus e soglie. Mostrare punti, segno e descrizione; distinguere contributo al totale dall’indice di area 0–100. Evitare grafici decorativi o radar come unico strumento decisionale.

### RF-27 · Navigazione degli approfondimenti [C / P]

Raggruppare le funzioni esistenti in Sintesi; Azioni e Action Plan; Registro segnalazioni; Analisi e scenari; Metodo; Strumenti ed export. Conservare cause e motivazioni, Toolbox Talk, Come ridurre il rischio, HSE Advisor, Scorecard e Toolkit. Da ogni alert si deve raggiungere l’evento o il dato che lo ha generato.

SPECIFICA DI PRODOTTO / 08

## Output operativi, export e archivio

### RF-28 · Azioni e Action Plan [C / P]

Per ogni azione mostrare priorità, causa o segnalazione collegata, proposta operativa, responsabile e scadenza da confermare. Le anomalie chiuse non devono produrre azioni di chiusura. Conservare la distinzione tra suggerimento e verifica effettuata. Proposta: introdurre un registro persistente con ID azione, stato Aperta/In corso/Chiusa, evidenza di chiusura, autore e data; tale capacità è nuova rispetto all’Action Plan non persistente descritto nella guida.

### RF-29 · Spiegazioni e simulazioni [C / P]

Collegare ogni motivazione agli input reali, senza dichiarare una root cause accertata. Gli scenari restano indipendenti e i benefici non si sommano automaticamente. Una simulazione non modifica la valutazione salvata. L’Advisor locale a regole deve spiegare il report senza presentarsi come validazione automatica delle misure operative.

### RF-30 · Salvataggio esplicito [C / P]

Calcola produce risultati temporanei; download produce file; solo “Salva e inserisci” alimenta lo storico. Dopo successo mostrare conferma, data e revisione. In caso di errore conservare i dati e consentire il tentativo successivo. Proposta tecnica: impedire duplicazioni dovute a doppio clic o ritrasmissione della stessa richiesta. “Non salvare” scarta la bozza corrente senza eliminare storico o documenti già scaricati.

### RF-31 · Esportazioni [C / P]

Mantenere Excel completo, PowerPoint e report Word; toolbox e checklist Word; sinottico PDF A3 e Word; calendario ICS; backup JSON. L’Excel include sintesi, contributi, Action Plan, NC, criticità, sensibilizzazioni, metodo, scenari, storico e input. Ogni export deve indicare cantiere, periodo, versione modello, revisione o stato temporaneo e data di generazione; deve riprodurre i valori visualizzati.

### RF-32 · Storico e confronti [C]

Usare l’ultima revisione per cantiere, mese e versione modello. Mesi mancanti: interruzione della linea, mai zero. Confrontare indice base, stesso mese concluso, stessa versione e target comune; motivare le esclusioni. Conservare tutte le revisioni. “Usa come base” richiede aggiornamento di periodo, eventi e stati, senza trascinare automaticamente le chiusure precedenti.

SPECIFICA DI PRODOTTO / 09

## Sinottici e calendario condiviso

### RF-33 · Pianificazione impresa [C / P]

Richiedere cantiere, impresa, periodo e attività. Per ogni attività: descrizione, giorni previsti, area, preposti, operatori e riferimento POS testuale obbligatorio; integrare gli ulteriori campi obbligatori già presenti. Verificare totali giornalieri e coerenza del periodo. L’importazione da documento o testo propone dati da verificare e non equivale a pubblicazione.

### RF-34 · Conferma e revisione [C]

Dopo “Verifica e prepara il sinottico”, risolvere le integrazioni. Richiedere la conferma dei dati, date, preposti e totali giornalieri e l’azione “Conferma e inserisci”. Solo l’esito positivo alimenta il calendario. Bozza, anteprima e download non pubblicano. La modifica di un piano esistente genera una revisione, mantenendo le precedenti; nella vista corrente usare l’ultima per impresa, cantiere e settimana.

### RF-35 · Consultazione [C / P]

Filtri per cantiere, impresa e settimana; settimana da lunedì a domenica. Ogni scheda mostra attività, impresa, preposto e area. Consentire accesso a dettaglio e allegati. Proposta: vista settimanale desktop e agenda giornaliera mobile, mantenendo i filtri. Mostrare data dell’ultimo aggiornamento e comando Aggiorna calendario.

### RF-36 · Significato dei dati [C]

La valutazione mensile non alimenta automaticamente il calendario e il calendario non compila automaticamente l’indice. La pubblicazione del sinottico non costituisce approvazione o autorizzazione al lavoro. Le firme seguono il processo applicabile. Un giorno senza attività pubblicate non dimostra assenza di lavoro reale. L’ICS è una fotografia dei filtri e della settimana esportata, senza aggiornamento automatico.

### RF-37 · Stati ed errori [C / P]

Distinguere nessuna pianificazione confermata, nessuna attività nel giorno, filtri senza risultati, piano precedente incompleto e indisponibilità dell’archivio. Un errore di connessione non deve apparire come calendario vuoto. I piani precedenti senza POS restano consultabili con avviso e richiesta di revisione.

### RF-38 · Condivisione [C / P]

Le pianificazioni e le valutazioni salvate devono essere disponibili tra sessioni distinte tramite archivio condiviso. Verificare la consultazione da una sessione separata dopo pubblicazione. I backup delle valutazioni e quelli dei sinottici restano distinti e riconoscibili.

SPECIFICA DI PRODOTTO / 10

## Design system e criteri di accettazione

### UI-01 · Aspetto e accessibilità [P]

Stile corporate ispirato ai cantieri: sfondo grigio #F3F4F6, testo antracite #20252B, navigazione #252A31 e azione principale arancio scuro #A63D00. Inserti arancio vivo #F97316 con testo scuro, mai bianco per testo ordinario. Colori di rischio sempre accompagnati da parole e valori. Tipografia leggibile, testo base 16 px, spaziatura su multipli di 8 px, campi alti almeno 44 px e larghezza dei contenuti controllata. Focus visibile, etichette associate ai campi, ordine di tabulazione logico e contrasto almeno 4,5:1 per il testo ordinario.

Desktop: barra laterale e massimo tre colonne; tablet: due; mobile: una, senza scorrimento orizzontale della pagina. Tabelle ampie con contenitore dedicato o schede. Usare icone uniformi accompagnate da testo, titoli brevi, un solo pulsante principale per passaggio e caricamenti con stato esplicito.

### QA-01 · Condizioni verificabili per il rilascio

| Caso | Esito atteso |
| --- | --- |
| Testi richiesti | Nessun massimale nei titoli NC e Stop Work; aiuti a destra; unica domanda sulle ispezioni HSEQ4ALL. |
| Validazioni | Scheda incompleta, conteggi negativi o mese futuro bloccano il calcolo indicando il campo. |
| Soglie | Una NC formale alta aperta: ≥61; due: ≥81; pericolo attuale: ≥81 anche con bonus massimo. |
| Detection | 0 ispezioni non causa errori; formula e contributo coincidono con il motore aggiornato. |
| Coerenza risultato | Contributi, correttivi, soglia e limite ricostruiscono il punteggio; fascia corretta sui confini. |
| Modifica e ricalcolo | Cambio input segnala risultato non aggiornato e richiede nuovo calcolo prima di salvarlo. |
| Archivio | Calcolo e download non salvano; doppio invio non duplica; errore conserva la bozza. |
| Confronti | Esclusi mese corrente, versioni e target differenti; mesi assenti non visualizzati a zero. |
| Calendario | Bozza assente; piano confermato visibile da altra sessione; revisione aggiorna la vista. |
| UI ed export | Uso a 375/768/1440 px e con tastiera; file coerenti con input e revisione visualizzati. |

### Sequenza di realizzazione [P]

P0: contratto di calcolo, testi, validazioni e salvataggio. P1: importazione strutturata immagini, uso mobile/tablet, calendario analitico ed export management secondo RF-39–RF-56. P2: account nominativi e Action Plan persistente. Verificare ogni rilascio con casi rappresentativi Wind, Solar e BESS e con confronto tra risultato precedente e nuovo a parità di input.

Riferimenti di ricostruzione: Guida operativa HSE Enel, 16/10/2026; schermate e richieste dell’utente del 19/10/2026. La presentazione metodologica di luglio è riferimento storico, non fonte dei coefficienti correnti.

SPECIFICA DI PRODOTTO / 11

## Lettura immagini: acquisizione assistita

Integrazione 1.1 • RF-39–RF-56. Le richieste di lettura migliorata, uso mobile/tablet, tema grigio/arancione, export management e calendario analitico sono consolidate [C]; le soluzioni operative e i valori obiettivo di questa integrazione sono proposte attuative [P]. Le nuove indicazioni grafiche sostituiscono la palette precedente. Il modello di rischio e le sue soglie restano quelli del requisito base.

### RF-39 · Obiettivo e flusso [C / P]

Trasformare foto, screenshot e PDF scansionati di sinottici in schede attività modificabili, ricostruendo righe e colonne. Il flusso deve essere: Carica → Controlla immagine → Estrai → Verifica dati → Inserisci nella bozza. La conferma del sinottico e la pubblicazione nel calendario rimangono passaggi successivi ed espliciti.

La versione documentata del codice legge le immagini con OCR su un unico blocco di testo, mentre riconosce la griglia per alcuni PDF. Il miglioramento richiesto deve conservare la struttura spaziale: l’estrazione di parole isolate non è sufficiente per assegnare giorni e persone a un’attività.

### RF-40 · Tipi di input e qualità [P]

Supportare JPEG, PNG e PDF sia digitali sia scansionati, anche multipagina. Per PDF digitali privilegiare testo e coordinate native; per le pagine immagine attivare OCR. Mostrare miniature, ordine delle pagine e possibilità di escludere duplicati. Acquisizione da fotocamera disponibile sui browser compatibili, con caricamento file sempre alternativo.

Prima dell’estrazione consentire rotazione, ritaglio della tabella e correzione della prospettiva; indicare sfocatura, riflessi, tagli o risoluzione insufficiente. Non ingrandire indiscriminatamente tutte le foto: il trattamento deve dipendere dalla qualità. Proposta iniziale: 15 MB/file, 5 pagine e budget di 20 megapixel per pagina prima dell’elaborazione; limiti da collaudare anche dopo decompressione, correzioni e ridimensionamento.

### RF-41 · Motore di lettura [P]

Riconoscere intestazioni, righe, colonne dei giorni, celle unite e testi su più righe. Separare riconoscimento dei caratteri e assegnazione ai campi. Se la struttura non è riconosciuta, proporre la mappatura manuale delle colonne; non applicare silenziosamente una mappatura per posizione. Il formato storico può avere 8 date: identificare ogni data reale, segnalare quelle fuori settimana e non comprimerle automaticamente in 7 giorni.

Elaborazione asincrona o con avanzamento per pagina, possibilità di annullare e limite di tempo esplicito. Un file non elaborabile deve lasciare utilizzabile la compilazione manuale. Non attivare nuovi servizi esterni per l’OCR senza una configurazione esplicita del relativo trattamento dei documenti.

SPECIFICA DI PRODOTTO / 12

## Lettura immagini: dati e revisione

### RF-42 · Contratto dei dati estratti [P]

| Gruppo | Campi da riconoscere e mantenere collegati |
| --- | --- |
| Documento | Cantiere, impresa, periodo, pagina di provenienza e revisione se presente. |
| Attività | Area/WTG, descrizione, affidataria, esecutrice, mezzi e riferimento POS. |
| Presidio | Preposto e contatto, senza scambiarli con i nominativi delle altre righe. |
| Date e persone | Data esplicita di ogni colonna e operatori per attività/giorno. Un segno di presenza non è un numero di operatori. |
| Condizioni operative | Interruzione area/strada, notturno, spazio confinato, lavori a caldo, interferenze, note e misure. |
| Provenienza | Valore originale, valore normalizzato, pagina e riquadro sorgente, stato di verifica e correzioni manuali. |

### RF-43 · Verifica assistita [P]

Su desktop affiancare immagine con zoom e schede estratte; selezionando un campo evidenziare la cella sorgente. Su mobile alternare Fonte e Dati mantenendo l’attività selezionata. Evidenziare “Da verificare”, “Mancante” e “Verificato”, usando testo e icone. Se il motore fornisce una confidenza OCR, identificarla come indicatore tecnico, senza presentarla come probabilità che il dato sia corretto.

Date, giorni/persone, preposto, impresa, POS e risposte sulle condizioni operative richiedono revisione esplicita. Celle vuote, trattini, illeggibili e valori assenti restano “Da integrare”: non diventano automaticamente zero o “No”. Non ricostruire nominativi, telefoni o POS per analogia. Anno e settimana devono essere confermati se ambigui.

### RF-44 · Controlli e importazione [P]

Verificare numeri interi non negativi, date effettive, righe duplicate, campi obbligatori e coerenza dei totali. Sommare gli operatori sulle attività solo se il modello li intende come persone distinte: una stessa persona impegnata su più attività non va contata due volte. Tenere distinto il totale per riga dalla forza lavoro giornaliera dichiarata; una discrepanza genera una richiesta di verifica, non una correzione arbitraria.

Il riepilogo deve indicare righe riconosciute, confermate, escluse e incomplete. Inserire nella bozza soltanto le righe selezionate; mantenere quelle incomplete identificabili e impedire la pubblicazione finché i dati obbligatori non sono risolti. Conservare le correzioni durante riestrazioni e impedire duplicazioni dello stesso import. La disponibilità delle immagini dopo la sessione deve seguire una politica esplicita; la sola anteprima non autorizza un’archiviazione permanente.

SPECIFICA DI PRODOTTO / 13

## Tablet, mobile e accessibilità

### RF-45 · Layout e interazione [C / P]

Utilizzo completo da desktop, tablet e smartphone in verticale e orizzontale, senza obbligare a ruotare il dispositivo. Sotto 768 px: una colonna, menu richiudibile, filtri in pannello e attività in schede; 768–1199 px: al massimo due colonne; da 1200 px: vista estesa. Sono breakpoint proposti da verificare sui contenuti reali. Il calendario mobile parte dall’agenda, non da sette colonne compresse.

Conservare filtri e input al cambio orientamento. Evitare trascinamento come unica modalità d’azione, informazioni disponibili solo al mouse, finestre fuori schermo e pulsanti nascosti dalla tastiera. Date con selettore e inserimento accessibile; campi numerici con tastiera appropriata. Le barre fisse non devono coprire contenuti o focus. Gestire rete interrotta e ripetizione del salvataggio senza duplicati; nessuna promessa di funzionamento offline senza apposita implementazione.

### RF-46 · Palette con ruoli distinti [C / P]

| Uso | Colore / abbinamento |
| --- | --- |
| Sfondo e superfici | #F3F4F6 e #FFFFFF; testo principale #20252B. |
| Navigazione | #252A31 con testo bianco. |
| Azione primaria | #A63D00 con testo bianco; arancio scuro per pulsanti. |
| Inserti cantiere | #F97316 con testo #20252B; bordi, selezioni e indicatori. |
| Aiuti e selezioni | #FFF0E0 con testo #A63D00; non usare il solo colore per il focus. |
| Stati di rischio | Colori semantici dedicati + nome dello stato + icona; arancio del marchio distinto da allarme. |

### RF-47 · Obiettivo WCAG 2.2 AA [C / P]

Richiedere conformità delle pagine e dei percorsi completi, incluse importazione, calendari ed errori. Verificare contrasto del testo ordinario ≥4,5:1, testo grande ≥3:1 e componenti/stati visivi pertinenti ≥3:1; reflow a 320 CSS px salvo contenuti bidimensionali essenziali, testo ingrandibile al 200%, tastiera, focus visibile e non oscurato, etichette e messaggi di stato accessibili. Target touch di progetto 44×44 CSS px, più ampio del minimo AA di 24×24 soggetto alle eccezioni del criterio 2.5.8.

La scelta dei colori non costituisce approvazione o certificazione. Il rilascio richiede verifiche automatiche e manuali dei criteri A e AA applicabili, con evidenze e correzione dei difetti bloccanti. Riferimento: W3C, Web Content Accessibility Guidelines 2.2, https://www.w3.org/TR/WCAG22/.

SPECIFICA DI PRODOTTO / 14

## Export aziendali per il management

### RF-48 · Due percorsi di lettura [C / P]

L’utente deve poter scegliere “Sintesi management” oppure “Report operativo completo”. La sintesi deve essere una presentazione aziendale leggibile in riunione, con messaggi decisionali e grafici selezionati; il report completo conserva registri, metodo ed evidenze. Non esportare semplicemente le schermate del tool.

### RF-49 · Struttura proposta della presentazione [P]

| Slide | Messaggio e contenuto |
| --- | --- |
| 1 · Apertura | Titolo, cantiere/perimetro, periodo, revisione e data. |
| 2 · Sintesi decisionale | Indice, fascia, variazione comparabile e tre punti di attenzione; dati mancanti espliciti. |
| 3 · Andamento | Trend e confronto omogeneo con contesto delle variazioni. |
| 4 · Determinanti | Contributi effettivi e soglie: cosa aumenta l’indice e cosa lo riduce. |
| 5 · Segnalazioni | NC aperte, gravità, ricorrenze e ritardi; distinguere NC formali e informali. |
| 6 · Coordinamento | Calendario sintetico, aree con compresenze e verifiche richieste. |
| 7 · Azioni e decisioni | Priorità, owner, scadenze, stato e decisioni richieste al management. |
| 8 · Metodo e qualità | Versione modello, periodo, copertura dati e limiti del confronto. |

### RF-50 · Standard visivo e formati [P]

PowerPoint modificabile in 16:9 e PDF corrispondente; usare gli stessi dati e filtri di origine. Titoli 28–36 pt, corpo 18–22 pt e note almeno 12 pt. Una conclusione per slide; massimo 3–5 indicatori chiave, grafici leggibili, etichette dirette e tabelle brevi. Contenuti eccedenti vanno in appendice o su più slide, senza ridurre progressivamente il testo. Palette grigio/arancione coerente, fondi chiari per stampa e nessun logo ufficiale inserito per deduzione.

Excel con foglio sintesi management, grafici e filtri, tabelle strutturate, intestazioni congelate, formati numerici coerenti e pagine di stampa ordinate; dati operativi in fogli dedicati. Word/PDF operativo con sintesi iniziale e dettagli successivi. Sinottico A3 leggibile su più pagine con intestazioni ripetute, senza comprimere tutto su una pagina. Esportazione settimanale del calendario coerente con i filtri e accompagnata da legenda.

### RF-51 · Coerenza e accessibilità dei file [P]

Ogni KPI deve mostrare denominatore, unità, fonte e periodo. Nessuna variazione se il precedente non è comparabile; dato assente diverso da zero. Escludere contatti personali non necessari alla sintesi management. Richiedere testi selezionabili, ordine di lettura, titoli e alternative testuali dei grafici dove supportati. Verificare accessibilità dei file separatamente da quella del web, senza attribuire automaticamente ai PDF la conformità del tool.

SPECIFICA DI PRODOTTO / 15

## Calendario condiviso: lettura analitica

### RF-52 · Viste complementari [C / P]

La vista iniziale deve rispondere a chi lavora, dove, quando e sotto quale presidio. Desktop: settimana con righe per area/WTG e gruppi per impresa; tablet: settimana compatta con dettaglio laterale o agenda; smartphone: agenda del giorno e navigazione tra giorni. Aggiungere elenco tabellare filtrabile e matrice Area × Giorno come alternative accessibili. Mese solo come panoramica della programmazione, senza dettaglio minuto delle attività.

### RF-53 · Filtri, ricerca e schede [P]

Filtri per cantiere, intervallo/settimana, impresa, area/WTG, attività e condizioni operative; ricerca per descrizione e preposto. Mostrare filtri attivi, numero risultati e “Azzera filtri”. Una scheda deve riportare attività, area, impresa, preposto, data, operatori dichiarati e badge testuali per notturno, caldo, confinato e interruzioni. Aprire dettaglio con POS, mezzi, note, revisione e sinottico sorgente.

Giorno corrente distinto dalla selezione. Non usare un colore diverso per ogni impresa: conservare pochi colori semantici, etichette e una legenda. In caso di molte attività usare “Mostra altre”, mantenendo conteggio e accesso al dettaglio. Intestazioni fisse dove utili; nessun testo troncato senza possibilità di leggerlo integralmente.

### RF-54 · Indicatori e verifiche di coordinamento [P]

Mostrare imprese operative per giorno, attività pianificate, aree interessate, forza lavoro giornaliera dichiarata e pianificazioni da integrare. Le card rispettano i filtri; dichiarare le regole di deduplicazione. Non chiamare “persone presenti” la somma degli operatori per attività se non è disponibile la loro unicità.

Segnalare “Compresenza da verificare” quando attività di imprese diverse ricadono nella stessa area e nello stesso giorno. Con orari mancanti non dichiarare una sovrapposizione temporale certa; aree vicine non sono automaticamente interferenti. Eventuali incompatibilità vanno basate su regole esplicite e motivate. Ogni indicatore deve aprire l’elenco degli eventi che lo compongono. Una segnalazione non costituisce valutazione delle interferenze né autorizzazione.

### RF-55 · Versioni e aggiornamento [P]

Utilizzare solo pianificazioni confermate e revisioni attive, con identificativo stabile del piano. Mostrare data di pubblicazione, revisione e ultimo aggiornamento della vista; rendere consultabile cosa è cambiato. Filtri condivisi tra viste e mantenuti durante l’analisi. Separare archivio indisponibile, filtri senza risultati e assenza di piani pubblicati. Export calendario e indicatori devono usare il medesimo insieme di revisioni.

SPECIFICA DI PRODOTTO / 16

## Collaudo e priorità della revisione 1.1

### RF-56 · Criteri misurabili di accettazione [P]

| Ambito | Verifica richiesta |
| --- | --- |
| OCR strutturale | Confronto con trascrizione manuale su almeno 20 sinottici rappresentativi: foto inclinate, screenshot, scansioni, celle unite e multipagina. Misurare campi corretti e righe/giorni assegnati correttamente, prima e dopo revisione. |
| Qualità OCR | Obiettivo iniziale ≥95% dei campi critici esatti su immagini leggibili; risultati separati per tipo documento. Soglia da validare sul campione, senza dichiararla già raggiunta. Nessun dato assente trasformato in valore certo. |
| Revisione e pubblicazione | Tutti i campi critici confermati o corretti; incompletezze bloccano la pubblicazione. Nessun import duplicato e nessuna correzione persa dopo riestrazione. |
| Dispositivi | Percorsi completi a 320/375/768/1024/1440 CSS px, entrambe le orientazioni e tastiera a schermo. Prova reale su iOS/Safari e Android/Chrome, oltre al desktop. |
| Accessibilità | Controlli automatici più tastiera, zoom, lettore di schermo e contrasto in tutti gli stati. Evidenze per i criteri WCAG A/AA applicabili, non soltanto un punteggio automatico. |
| Calendario | Con almeno 10 imprese e 100 attività settimanali: filtri coerenti, conteggi riproducibili, ultima revisione unica e dettaglio raggiungibile in massimo due azioni dalla scheda. |
| Export | Nessun taglio o sovrapposizione; grafici leggibili alla dimensione di presentazione. PPTX editabile e PDF coerente, sinottico A3 verificato; tutti i KPI riconciliati con il tool. |
| Usabilità | Almeno 5 utilizzatori rappresentativi: trovare attività di un’impresa, preposto e compresenza entro 60 secondi ciascuno senza assistenza. Registrare errori e necessità di aiuto. |

### Ordine di attuazione

1. Fissare campione sinottici, struttura dei dati e criteri di lettura. 2. Introdurre palette e componenti responsive. 3. Realizzare estrazione strutturata e revisione assistita. 4. Migliorare viste, filtri e indicatori del calendario. 5. Realizzare i template management e verificare i file. 6. Eseguire collaudo funzionale, accessibilità e prova con utilizzatori.

Il rilascio deve preservare valutazioni e pianificazioni archiviate, con migrazione esplicita dei nuovi campi e assenza di cambiamenti al punteggio dovuti al solo redesign. La disponibilità del sorgente documentato del 16 ottobre permette l’analisi tecnica; l’allineamento con la versione effettivamente pubblicata va verificato prima di applicare le modifiche.

Riferimenti: HSE Risk Platform, codice completo, versione documentale 3 del 16/10/2026; requisito 1.0 e richieste del 19/10/2026; W3C WCAG 2.2, https://www.w3.org/TR/WCAG22/.

SPECIFICA DI PRODOTTO / 17

## Passaggio a Codex: perimetro e piattaforma

Revisione 1.2 • I quattro nuovi moduli richiesti sono Sopralluogo rapido, Preparazione riunione, Toolbox dalle attività e Documenti per area con mappa KMZ e segnaletica. Sono funzioni facoltative e indipendenti: nessuna richiede di completare una valutazione del rischio. Non introdurre modifiche ai pesi, alla detection o alle formule rifiutate nella conversazione.

### RF-57 · Regole di sviluppo e prevalenza

Questo documento e la copia Markdown HSE_SPEC_CODEX.md sono la medesima specifica. Per conflitti prevale la revisione 1.2; RF-57–RF-76 integrano RF-01–RF-56. Le soluzioni tecniche indicate come proposte sono default attuativi: Codex può risolvere scelte reversibili motivandole, senza bloccare ogni passaggio. Mantenere distinti requisiti di prodotto e dettagli metodologici ancora da verificare nel sorgente del calcolo.

### RF-58 · Architettura di riferimento

WordPress è il CMS, AlterVista il possibile hosting, Elementor un editor visuale opzionale: non sono tre piattaforme equivalenti. Sviluppare il plugin autonomo hse-risk-platform in PHP e JavaScript, con dati in MySQL/MariaDB tramite WordPress. Esporre la UI con shortcode [hse_platform]; aggiungere, se Elementor è presente, un widget contenitore che richiama la stessa UI. Disattivare Elementor non deve eliminare dati o funzioni del plugin.

Usare componenti responsive e CSS circoscritto al plugin; applicare palette grigio/arancione, terminologia italiana e criteri di accessibilità già definiti. Non mettere logica applicativa in snippet di pagina o nel tema. Il pacchetto ZIP deve contenere asset già compilati: Node, Composer e strumenti di sviluppo possono servire alla build locale, non devono essere necessari sul piano hosting per l’utilizzo ordinario.

### RF-59 · Verifica dell’hosting e portabilità

Prima della consegna verificare sul piano effettivo: installazione plugin personalizzati, versioni PHP/WordPress, estensioni ZIP/XML/immagini, database, HTTPS, upload/memoria/tempi e regole cache. Nessun requisito di processo Python, Tesseract o servizio Node permanente sul server AlterVista. Proporre OCR in browser con worker e italiano oppure un adattatore server opzionale; l’OCR scelto deve superare RF-39–RF-44, non limitarsi al testo libero.

Le esportazioni possono essere prodotte nel browser o in PHP con dipendenze incluse e compatibili. Eventuali librerie cartografiche, OCR e generazione file devono essere versionate e accompagnate da licenze; risorse linguistiche caricate su richiesta e cache controllata. Non rendere il prodotto dipendente da servizi a pagamento o account esterni non richiesti.

SPECIFICA DI PRODOTTO / 18

## Sopralluogo rapido da smartphone

### RF-60 · Flusso minimo

Dalla pagina del cantiere premere “Nuovo sopralluogo”, scegliere l’area/WTG oppure “Area da specificare”, aggiungere una nota e facoltativamente foto. Se cantiere e area sono già selezionati non richiederli di nuovo. La tastiera con dettatura del dispositivo può alimentare la nota; la registrazione di audio non è necessaria. Obiettivo di progetto: salvare una scheda essenziale in meno di un minuto, escluso il tempo necessario a scattare le foto.

Per salvare servono cantiere e almeno una nota o una foto. Autore e data sono automatici. Area, tema, impresa, riferimento a un’attività e dettagli si possono integrare in seguito. Non obbligare a compilare checklist, gravità, responsabile e scadenza per acquisire un semplice appunto.

### RF-61 · Scheda ed evidenze

Campi: ID, cantiere, area, data osservazione, autore, nota, allegati, tema facoltativo e collegamenti a calendario, documenti o mappa. Distinguere foto originale e copia annotata; consentire frecce, cerchi e breve testo senza alterare l’originale. Ridimensionare le copie di visualizzazione, verificare formato e dimensione, rendere visibile il progresso upload. Geolocalizzazione solo su azione esplicita, modificabile e non obbligatoria; evitare coordinate EXIF condivise involontariamente negli export.

Stati semplici: Bozza e Registrato. La nota può essere integrata con revisione o correzione tracciata. Eliminare una bozza non tocca le osservazioni registrate. Connessione interrotta: segnalare mancato invio, conservare quanto possibile nella sessione e consentire il retry con lo stesso identificativo per evitare duplicati. Non promettere archiviazione offline automatica di foto sul dispositivo.

### RF-62 · Riutilizzo senza doppio inserimento

Da una scheda registrata offrire “Porta in riunione”, “Collega a un documento” e “Prepara segnalazione”. Quest’ultima apre una bozza NC/criticità con dati già riportati e riferimento all’osservazione; non crea direttamente una NC formale né una registrazione HSEQ4ALL. La stessa osservazione non deve essere ricopiata ogni volta come nuovo record indipendente.

L’utente può scaricare la scheda in PDF e includerla negli allegati del verbale. Il sopralluogo rapido non modifica da solo il Risk Index: un’eventuale segnalazione entra nel calcolo solo mediante il flusso di valutazione previsto, con canale, periodo e campi obbligatori verificati.

### Accettazione AT-60

Da 375 CSS px salvare nota e due foto, riaprire la scheda e trovare gli allegati. Retry dello stesso salvataggio: un solo record. “Porta in riunione” mantiene il riferimento alla scheda, senza richiedere la riscrittura della nota.

SPECIFICA DI PRODOTTO / 19

## Preparazione della riunione di coordinamento

### RF-63 · Ordine del giorno assistito

Selezionare cantiere e settimana, poi “Prepara riunione”. Proporre attività e imprese dai sinottici confermati, compresenze da verificare e sopralluoghi selezionati dall’HSE. Mostrare fonte, revisione e data di aggiornamento di ogni elemento. Consentire inclusione/esclusione, riordino e aggiunta di argomenti manuali. I dati del calendario alimentano una proposta e non un verbale di fatti già avvenuti.

### RF-64 · Conduzione e registrazione

La scheda riunione contiene data, titolo, luogo/modalità, partecipanti inseriti o selezionati, ordine del giorno e argomenti. Ogni argomento presenta contesto sintetico, riferimento all’attività/area e campo per decisione, responsabile e scadenza, questi ultimi richiesti solo quando si registra un’azione. Permettere di annotare decisioni durante la riunione anche da tablet.

Stati: Preparazione, Da verificare, Finalizzato. Il passaggio a Finalizzato richiede conferma esplicita del contenuto, senza inventare presenze o firme. Modifiche successive producono una revisione con motivazione. Salvare la fotografia degli input usati: un aggiornamento del calendario non deve riscrivere un verbale già finalizzato. Offrire un comando di aggiornamento con confronto per le riunioni ancora in preparazione.

### RF-65 · Output e collegamenti

Generare ordine del giorno e verbale Word/PDF con intestazione cantiere, periodo, revisione, partecipanti dichiarati, argomenti, decisioni e tabella azioni. Consentire la sintesi delle decisioni per il management, senza trasferire automaticamente contatti e dettagli personali superflui. Le azioni rimandano alla riunione e alle osservazioni originali, evitando copie scollegate.

Consentire download e predisposizione del testo di accompagnamento; nessun invio email, convocazione o notifica a persone senza una funzione e un comando esplicitamente richiesti. Il verbale non deve essere presentato come firmato o condiviso solo perché finalizzato nel tool.

### Accettazione AT-63

Con tre imprese e dieci attività confermate, preparare un ordine del giorno, escludere due voci e aggiungere una nota da sopralluogo. Finalizzare una decisione con un’azione; verificare che un successivo cambio di sinottico non alteri il verbale né crei un duplicato dell’azione.

### UX essenziale

Tre schermate: Seleziona contenuti, Conduci/annota, Rivedi ed esporta. Non imporre la compilazione di un report completo per scaricare un semplice ordine del giorno. Bozza sempre riconoscibile e recuperabile dopo una navigazione interna.

SPECIFICA DI PRODOTTO / 20

## Toolbox dalle attività previste

### RF-66 · Proposta contestuale

Da attività, calendario o scheda area scegliere “Prepara toolbox”. Il sistema propone una traccia pertinente usando attività selezionate, condizioni operative dichiarate, area, interferenze da verificare e documenti collegati. Mostrare gli input utilizzati e quelli mancanti. Non trasformare una condizione non compilata in assenza del rischio.

Nel primo rilascio usare modelli revisionati e regole esplicite di abbinamento tema–attività, riutilizzando il catalogo pertinente del tool. Non richiedere un servizio AI esterno per la funzione base. Un’eventuale integrazione futura non può inventare prescrizioni, riferimenti normativi, distanze, DPI o autorizzazioni non supportati dalle fonti.

### RF-67 · Contenuti e personalizzazione

Traccia breve orientata alla discussione: attività prevista, condizioni da verificare prima dell’avvio, rischi pertinenti, misure presenti nei documenti selezionati, domande alla squadra, criteri per interrompere e richiedere chiarimenti. Ogni misura estratta da un documento deve indicare riferimento e revisione; senza testo disponibile mostrare un invito alla verifica, non una prescrizione attribuita al documento.

L’HSE può modificare la traccia, selezionare i temi e aggiungere foto o schema dell’area. Obiettivo: scheda di 1–2 pagine, leggibile da mobile e stampabile. Un toolbox pronto è un supporto al confronto e non un’autorizzazione alla lavorazione.

### RF-68 · Preparato e svolto sono stati distinti

Stati: Preparato e Svolto. Generare o scaricare il toolbox non registra sensibilizzazioni. Solo “Registra incontro svolto” apre data effettiva, tema, numero incontri, destinatari e copertura nota o non disponibile. Consentire l’inserimento di evidenza. La registrazione resta separata dai bonus del Risk Index: proporre il riuso nella valutazione mensile, evitando doppi conteggi e applicando soltanto le regole già previste.

Conservare un identificativo dell’incontro e collegarlo al toolbox sorgente. Più download dello stesso materiale non generano incontri aggiuntivi. I partecipanti non devono essere nominativi per obbligo del software se è sufficiente un dato aggregato nel processo applicabile.

### Accettazione AT-66

Selezionare una lavorazione di scavo e un’attività di sollevamento, verificare la pertinenza dei temi e modificare la traccia. Scaricare due volte: zero incontri registrati. Registrare un incontro effettivamente svolto: un solo record riutilizzabile nel mese corretto, con copertura assente distinta da zero.

SPECIFICA DI PRODOTTO / 21

## Documenti collegati alle aree e mappa KMZ

### RF-69 · Fascicolo essenziale per area

Aprendo una WTG, area BESS, campo FV, accesso o site camp, consultare i collegamenti utili: layout, viabilità, emergenze, elaborati e documenti selezionati dall’HSE. Preferire link all’archivio esistente; caricamento di una copia disponibile quando necessario. Un link protetto mantiene le autorizzazioni del sistema di origine e non va descritto come accessibile a tutti.

Metadati minimi: titolo, cantiere, area o più aree, categoria, URL o allegato, revisione dichiarata, data documento e stato Corrente/Superato. Un unico documento può appartenere a più aree senza duplicare il file. Mostrare chi ha indicato la revisione come corrente; non dedurla dal solo nome del file. Ricerca per titolo e filtri per categoria/area. Allegati HSE riservati non pubblici nella normale libreria media WordPress.

### RF-70 · Importazione KMZ/KML

Caricare KMZ o KML e mostrare anteprima dei livelli e degli oggetti prima del salvataggio. Gestire Point, LineString, Polygon, MultiGeometry e cartelle; leggere nomi, attributi e stili compatibili. Normalizzare in GeoJSON WGS84: ordine longitudine/latitudine, eventuale quota separata e nessuna conversione silenziosa delle linee in strade.

Riconoscere il KML principale; se più candidati sono ambigui chiedere la selezione. Trattare GroundOverlay e immagini interne come livello opzionale solo quando georeferenziazione e rotazione sono supportate e collaudate; in caso contrario indicare la funzione non supportata, senza posizionare l’immagine a caso. Elencare gli oggetti non importati. Nessun caricamento automatico di NetworkLink o risorse remote contenute nel KMZ.

### RF-71 · Immagine corrispondente e fonte cartografica

Dopo l’importazione inquadrare le geometrie e produrre una vista tecnica 2D esportabile, con sfondo neutro sempre disponibile. Aggiungere uno sfondo cartografico o satellitare solo se configurato, tecnicamente disponibile e con termini d’uso compatibili con visualizzazione ed export. Un KMZ non garantisce la presenza di immagini satellitari e non consente di ricostruire strade o confini mancanti.

L’utente può classificare gli oggetti come WTG, area, strada, cavidotto o altro e correggere nomi e associazioni. Conservare geometria sorgente e classificazione separatamente. Un cavidotto non è una strada; il colore del tracciato non determina la categoria. Collegare le geometrie alle aree tramite ID stabili scelti o confermati dall’utente, non solo per uguaglianza dei nomi.

SPECIFICA DI PRODOTTO / 22

## Segnaletica sulla mappa ed esportazione

### RF-72 · Inserimento libero ma tracciabile

Attivare la modalità Modifica; scegliere un simbolo da una libreria revisionata o una semplice annotazione, quindi posizionarlo con tocco/clic. Consentire spostamento, orientamento, etichetta, note, dimensione grafica e collegamento a un’area/documento. Alternative al trascinamento: modifica coordinate e comandi di spostamento. Consentire annullamento dell’ultima modifica e separare consulta da modifica per evitare spostamenti involontari.

Categorie iniziali proposte: accesso, divieto, obbligo, avvertimento, emergenza, punto di raccolta, DAE e indicazione di direzione. Non attribuire conformità normativa a simboli disegnati liberamente: i pittogrammi con tale qualificazione richiedono un catalogo verificato e licenziato. Annotazioni e simboli personalizzati devono essere riconoscibili come tali.

Ogni elemento ha ID, tipo simbolo, coordinate, orientamento, area, nota, stato Proposto/Da posizionare/Posizionato/Da verificare, data e autore. La selezione di “Posizionato” è dichiarata dall’utente e può avere una foto di riscontro; la presenza del simbolo nella tavola non dimostra l’installazione sul campo. Modifiche e salvataggi generano una revisione del piano.

### RF-73 · Tavola e persistenza

Esportare PNG e PDF A3/A4 con titolo, cantiere, data, revisione, legenda, oggetti selezionati, segnali ed eventuale attribuzione cartografica. Freccia nord e scala solo se calcolate coerentemente con proiezione, inquadratura e dimensione di stampa. Impostare etichette leggibili, sfondo chiaro e pochi colori; generare riquadri di dettaglio se necessario. Le geometrie importate devono restare separabili dalla segnaletica aggiunta.

Conservare coordinate, collegamenti e stile in dati strutturati; un PNG non deve essere l’unico archivio. Prevedere backup JSON/GeoJSON con versione schema per ripristinare e modificare il piano; esportazione KML di geometrie e segnali come formato aggiuntivo, dichiarando eventuali perdite di stile. Dopo il reload i simboli devono ricadere nelle stesse coordinate, anche cambiando zoom.

### Accettazione AT-70

Importare un KMZ di prova con 7 WTG, un cavidotto, una strada e un poligono. Confermare le categorie, collegare un documento a WTG6, aggiungere due segnali e modificare il loro orientamento. Ricaricare la pagina e verificare coordinate e link; esportare una tavola leggibile. Senza basemap disponibile, ottenere comunque la tavola vettoriale. Un KMZ corrotto o non supportato deve dare un errore specifico, non una mappa apparentemente corretta.

SPECIFICA DI PRODOTTO / 23

## Contratto dati e relazioni per Codex

### RF-74 · Entità comuni

Usare ID stabili, site_id per i dati di cantiere, created_at/updated_at in UTC, autore e numero versione per aggiornamenti concorrenti. Visualizzazione Europe/Rome; date del calendario senza conversioni che spostino il giorno. Riutilizzare gli ID di cantiere, area, impresa, attività e segnalazione in tutti i moduli. Le relazioni devono essere verificabili lato server.

| Entità / relazioni | Campi essenziali aggiuntivi |
| --- | --- |
| Site, Area, Membership | Area.site_id; nome e tipo; Membership.user_id/site_id/company_id e permessi. |
| Observation → Site/Area | note, observed_at, attachments[], status, author_id, activity_id opzionale. |
| Meeting → Site | meeting_date, participants dichiarati, status, source_snapshot e revision. |
| MeetingItem → Meeting | source_type/source_id opzionali, testo, ordine, decisione; eventuale action_id. |
| Action → fonte | description, owner, due_date, status, evidence; sorgente osservazione o riunione. |
| Toolbox → Site/Attività | template_id/version, content, source_refs[], status; incontri come entità separati. |
| ToolboxSession → Toolbox | held_on, topic, count, recipients/coverage opzionali, evidence, assessment_link. |
| Document + AreaDocument | URL privato o file protetto, category, declared_revision, status; relazione molti-a-molti con Area. |
| MapRevision → Site | source_asset, layers/GeoJSON, camera, basemap_id, revision, parent_revision. |
| MapFeature + Sign | feature_id stabile/area_id; segnale con coordinate, bearing, type, label, state e document_refs. |
| Asset / ExportSnapshot | tipo, hash e controlli accesso; snapshot di dati, filtri, revisioni e versione modello usati per l’export. |

### Aggiornamenti e migrazioni

Proposta: repository PHP con tabelle del plugin create/migrate tramite API WordPress e prefisso $wpdb; JSON per snapshot e contenuti flessibili. Codex può adottare custom post type privati se motivato e senza perdere permessi per cantiere, versioni e relazioni. Non introdurre un secondo archivio separato in localStorage: il browser conserva solo stato temporaneo e lavori non ancora inviati, con comportamento esplicito.

Concorrenza: inviare expected_version; un aggiornamento su versione superata restituisce conflitto e permette il confronto senza sovrascrivere. I retry con stesso request_id devono essere idempotenti. Uninstall e aggiornamento plugin non eliminano dati automaticamente; importazioni e migrazioni devono avere anteprima, backup ed esito per record.

SPECIFICA DI PRODOTTO / 24

## API, permessi e dipendenze

### Contratti API proposti

Namespace REST /hse/v1. Endpoint leggibili e versionati; paginazione, filtri site_id/area_id/date e risposta uniforme. Ogni richiesta con ID deve verificare l’accesso al relativo cantiere, anche se l’ID è valido. Non è sufficiente nascondere una voce nel menu.

| Risorsa | Operazioni essenziali |
| --- | --- |
| /sites e /areas | GET elenco autorizzato e dettaglio; gestione anagrafica per utenti abilitati. |
| /observations | GET/POST; PATCH /{id} con versione; azioni esplicite per riuso in riunione o segnalazione. |
| /meetings | GET/POST/PATCH; POST /prepare per proposta; /{id}/finalize con snapshot. |
| /toolboxes | GET/POST/PATCH; POST /prepare; /{id}/sessions per incontro svolto. |
| /documents | GET/POST/PATCH; relazioni area; download tramite autorizzazione. |
| /maps/import e /maps | Import preview con limiti; conferma import; GET/PATCH revisioni; gestione features/signs. |
| /exports | POST snapshot/formato; stato di generazione e download autorizzato se asincrono. |

### Autorizzazioni e gestione file

Ruoli applicativi: amministratore configurazione, HSE referente dei cantieri assegnati, HSE impresa limitato al proprio perimetro, lettore autorizzato. HSE impresa modifica i propri dati; la visibilità condivisa dei piani e delle aree è configurata dal referente. Foto, note interne e documenti riservati non diventano condivisi per il solo collegamento a un’attività del calendario.

Usare autenticazione WordPress, capability e appartenenza al cantiere, nonce per richieste browser, validazione/sanitizzazione, output escaping e query preparate. Allegati privati protetti anche dall’accesso diretto all’URL: la normale media library pubblica non basta. Cache e indicizzazione escluse dalle pagine/API riservate. Segreti solo sul server; nessuna password condivisa incorporata nel codice o nei prompt.

KMZ: verificare formato ZIP, percorsi normalizzati, numero file, dimensione totale decompressa e rapporto di compressione; bloccare path traversal, eseguibili, XML con entità esterne e markup attivo nelle descrizioni. NetworkLink disabilitati. File non fidati e SVG caricati non devono poter eseguire script. Limiti iniziali configurabili: 15 MB compressi, 50 MB decompressi, 200 file e 10.000 feature, da collaudare sul piano reale.

### Dipendenze critiche

Libreria mappe 2D con licenza compatibile e alternativa tabellare accessibile; parser KML/ZIP; OCR con lettura tabellare; generatori PPTX/PDF/XLSX/DOCX. Verificare compatibilità e licenze nelle versioni scelte; segnalare la funzione degradata quando manca una capacità, senza dichiarare completata una funzione simulata.

SPECIFICA DI PRODOTTO / 25

## Consegna, sequenza e verifica Codex

### RF-75 · Percorso di implementazione

0. Leggere tutta la specifica e ispezionare repository e runtime; creare matrice requisito→componente→test. 1. Costruire plugin, permessi, anagrafiche, schema e navigazione responsive. 2. Sopralluogo rapido e documenti per area. 3. Mappa KMZ con segnali ed export. 4. Riunioni e toolbox, riutilizzando attività/aree. 5. Migliorare sinottici, calendario e output management della revisione 1.1. 6. Portare o integrare il Risk Index e lo storico dopo verifica dell’algoritmo originario.

Le fasi organizzano il lavoro e non riducono il perimetro concordato: registrare ogni requisito come Completato, Parziale o Bloccato con evidenza. Se mancano sorgenti del calcolo, non inventare coefficienti né importare quelli obsoleti; completare i moduli indipendenti e rendere indisponibile il solo risultato non verificabile. Se esiste un repository mantenuto, lavorare lì e preservare dati e comportamenti compatibili.

### RF-76 · Definition of Done

Consegnare plugin ZIP installabile e codice completo, README con installazione WordPress/AlterVista e inserimento shortcode/Elementor, elenco versioni e dipendenze, migrazioni, dati demo sintetici, test e istruzioni di ripristino. Nessun servizio avviato sul computer di sviluppo deve essere requisito nascosto per l’uso sul sito. Pubblicazione in produzione distinta dalla preparazione del pacchetto.

| ID test | Esito atteso |
| --- | --- |
| AT-57 · Installazione | Attivazione senza Elementor; shortcode funzionante; con Elementor presente stessa UI e stessi dati. |
| AT-60/63/66 | Superati i percorsi di sopralluogo, riunione e toolbox delle pagine 18–20, compresi riuso e stati. |
| AT-69/70 | Documento associato a più aree; import KMZ, classificazione, segnali persistenti e tavola senza basemap. |
| AT-74 · Integrità | Nessun duplicato con retry; conflitto su versione superata; date stabili nei cambi ora legale/solare. |
| AT-74 · Accessi | Utente del cantiere A non legge/modifica B via URL, API o allegato; lettore non scrive; impresa rispetta il proprio perimetro. |
| AT-74 · File | Rifiuto KMZ con path traversal, XML attivo o decompressione eccessiva; errori leggibili e dati precedenti intatti. |
| AT-76 · UX/export | Percorsi completi su mobile/tablet; verifiche WCAG previste; output aperti e controllati nei formati finali. |

### Fonti tecniche da consultare durante lo sviluppo

WordPress: developer.wordpress.org/plugins/; developer.wordpress.org/apis/shortcode/; developer.wordpress.org/rest-api/extending-the-rest-api/adding-custom-endpoints/. Elementor: developers.elementor.com/docs/getting-started/first-addon. AlterVista: it.altervista.org/caratteristiche-hosting-wordpress-gestito.php. KMZ: developers.google.com/kml/documentation/kmzarchives. Accessibilità: www.w3.org/TR/WCAG22/. Verificare nuovamente documentazione e piano hosting al momento dell’implementazione.
