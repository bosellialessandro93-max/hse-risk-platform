# 0.3.0 — redesign UX/UI, 20/10/2026

- Design system navy/blu/teal, dashboard e cantieri con tre SVG originali, sidebar desktop/menu mobile, breadcrumb e form guidato con progressione e navigazione.
- KPI dei risultati ed esportazioni evidenti; aiuti NC/detection e logiche esistenti conservati.
- Template WordPress a pagina intera opzionale, senza cambiare tema o homepage.
- Focus, skip link, reduced motion, indicatori di attività; protezione dalle risposte di schermate precedenti e selezione persistente del cantiere creato.
- Nessuna modifica a motore 2.0.0, API, schema 1, cataloghi, autorizzazioni o generatori degli export. PHP minimo 8.0.30.
- Esiti e limiti: REDESIGN_0_3_0.md e REDESIGN_QA.json.

# 0.2.1 — compatibilità PHP 8.0.30

- Requisito PHP corretto a 8.0.30 dopo verifica reale, non per sola modifica del metadato.
- Parsing di tutti gli otto file e disponibilità delle 107 funzioni PHP/WordPress controllati sul runtime esatto. Nessuna API/sintassi esclusiva di 8.1 riscontrata; nessun polyfill o coefficiente sostitutivo aggiunto.
- Attivazione con controllo esplicito delle estensioni richieste; ZIP mancante produce un messaggio e non modifica le registrazioni.
- Ambiente di test PHP 8.0.30 isolato e test parametrizzati per container/URL; attese del test tastiera corrette per attendere l’inizializzazione completa.
- Installazione con Plugin_Upgrader WordPress, quattro tabelle InnoDB su database nuovo/prefisso personalizzato e conservazione dopo riattivazione. Riprodotto l’errore PHP 8.1 del vecchio ZIP.
- Versione/schema del modello, formule, librerie e bundle JavaScript invariati. Nessuna migrazione distruttiva o pubblicazione sul sito reale.
- Corretto il percorso del pacchetto nelle istruzioni; conservato lo ZIP 0.2.0 e il suo checksum.

# 0.2.0 — 20/10/2026

- Motore PHP 2.0.0 dal DOCX dell'utente: cataloghi, curve, detection descrittiva, Stop Work, sensibilizzazioni, soglie e contesto. Nessun coefficiente nuovo; confronto con il sorgente Python e sei scenari originali.
- Calcolo temporaneo, stato modificato, salvataggio esplicito con hash/versione e retry idempotenti. Storico conserva le Saved anche durante nuove bozze; trend e confronto omogeneo con esclusioni motivate.
- Sintesi/driver/cascata, fonti e azioni collegate, export numerici, grafico PowerPoint modificabile, Excel con grafico raster e dati dedicati. Sinottico A3 tabellare multipagina, Word strutturato, verbali con foto da snapshot.
- OCR con griglie/bande di riga e celle multilinea, otto date, revisore Fonte/Dati, zoom e correzioni conservate. Diagnostica qualità euristica, con revisione umana obbligatoria.
- Calendario con elenco tabellare, vista per area e Mostra altre; stili KML locali e selezione oggetti/dimensioni segnali nelle tavole.
- Corretti riferimenti a variabili dell'editor negli elenchi riunioni/eventi. Widget Elementor opzionale, stesso shortcode.

Aggiornamento additivo, schema database invariato (1). Nessuna cancellazione di bozze, dati o revisioni. Le vecchie lavorazioni libere vanno ricondotte esplicitamente al catalogo prima del calcolo; `Scavo` e maiuscole sono normalizzati. Nessuna migrazione automatica della vecchia app Streamlit o di HSE-Advisor. Nessuna pubblicazione in produzione.
