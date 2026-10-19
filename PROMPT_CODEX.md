# Prompt operativo per Codex — sviluppo completo da zero di HSE Risk Platform

## Come usarlo

1. Apri in Codex una cartella vuota per il nuovo plugin oppure una cartella dedicata nel repository WordPress. Non è necessario avere già un tool funzionante.
2. Metti nella cartella `HSE_SPEC_CODEX.md` e questo file. Il documento `HSE_Risk_Index_Requisito_Completo.docx`, revisione 1.2, è l'edizione consultabile della stessa specifica.
3. Se disponibili, aggiungi il sorgente aggiornato del tool Streamlit, le dipendenze e uno o più KMZ/sinottici di prova senza credenziali. Non caricare password, token o file di configurazione con segreti.
4. Incolla il testo della sezione seguente in Codex. I dati del piano hosting possono essere aggiunti in fondo se già noti; se assenti, Codex deve preparare un pacchetto portabile e documentare le verifiche rimaste.

---

## Testo da incollare in Codex

Realizza DA ZERO l’INTERO tool HSE Risk Platform, come nuovo prodotto completo e autonomo, seguendo integralmente il file allegato `HSE_SPEC_CODEX.md`, revisione 1.2 del 19 ottobre 2026. Se il file è fornito come allegato anziché nel repository, individua prima il suo percorso disponibile. Leggi il contenuto completo, incluse tabelle, vincoli, requisiti RF-01–RF-76 e test AT. Usa gli ID per tracciare l'implementazione.

L'obiettivo di questo incarico è consegnare software funzionante, installabile e verificato. Procedi dall'analisi all'implementazione e ai test, senza fermarti a una proposta, a un elenco di plugin o a un mockup. Crea tutto il codice applicativo necessario: frontend, backend, database, autenticazione, API, calcolo, importazioni, calendario, nuovi moduli ed esportazioni. Non presumere che le funzioni precedenti siano già implementate. Se il repository contiene altro lavoro, crea una cartella o un ramo dedicato e non cancellarlo; segui gli AGENTS.md applicabili.

### 0. Perimetro completo obbligatorio — nessuna funzione preesistente da dare per acquisita

Questa istruzione richiede la ricostruzione completa del prodotto. Non è un incarico limitato alle ultime funzionalità, un aggiornamento del vecchio Streamlit, un semplice restyling o una landing page. Il risultato deve essere installabile su una nuova installazione WordPress compatibile e funzionare senza la vecchia app.

Implementa tutti i seguenti ambiti secondo i dettagli della specifica:

1. Accesso, utenti, ruoli, assegnazioni ai cantieri e separazione dei dati per impresa.
2. Anagrafiche cantieri Wind/Solar/BESS, aree/WTG, imprese e navigazione delle aree HSE Enel e HSE impresa.
3. Valutazione mensile completa: attività, interferenze, organizzazione, copertura HSE, ispezioni HSEQ4ALL, NC formali/informali, Stop Work, sensibilizzazioni, esposizione e validazioni.
4. Motore Risk Index verificabile: indice base e contestualizzato, contributi, bonus, soglie, versioni e dettaglio del calcolo.
5. Risultati e strumenti: sintesi, alert, Action Plan, registro segnalazioni, cause e motivazioni, scenari, scorecard, Advisor locale, toolbox e checklist/Toolkit.
6. Salvataggio esplicito, bozze, revisioni, storico mensile, confronto cantieri e backup/ripristino.
7. Percorso HSE impresa: compilazione attività e sinottici, totali giornalieri, preposti, riferimento POS, validazione, conferma e revisioni.
8. Importazione di immagini, PDF e testo con riconoscimento strutturale del sinottico e revisione assistita.
9. Calendario condiviso completo: viste responsive, filtri, ricerca, matrice aree/giorni, indicatori, compresenze da verificare e allegati.
10. Sopralluogo rapido da smartphone con foto, note e riutilizzo nei flussi successivi.
11. Preparazione e gestione della riunione di coordinamento con ordine del giorno, verbale e azioni collegate.
12. Toolbox contestuali alle attività, personalizzazione e registrazione distinta degli incontri svolti.
13. Documenti per area e mappa da KMZ/KML con geometrie, segnali modificabili, coordinate persistenti, revisioni e tavole esportabili.
14. Tutti gli export previsti: PPTX management, PDF, Word, Excel, sinottico A3, toolbox/checklist, calendario ICS, tavole PNG/PDF e backup strutturati.
15. Design grigio/arancione, uso completo desktop/tablet/mobile, accessibilità, protezione dei file, migrazioni, test e pacchetto ZIP installabile.

Gli ambiti sono obblighi di consegna, non alternative. Il carattere facoltativo di una funzione per l’utilizzatore non autorizza a ometterne lo sviluppo. Le fasi servono a organizzare il lavoro: non limitarti al primo incremento o ai punti 10–13. Una funzionalità è completa solo se collegata a dati reali persistenti, permessi, validazioni e output funzionanti, quando richiesti. Non segnare il lavoro complessivo come concluso finché esistono requisiti non implementati: completa le parti possibili e riporta separatamente ogni impedimento effettivo.

Il codice precedente, se fornito, è materiale di riferimento per comportamento e formule, non una dipendenza di esecuzione. Puoi portare e verificare gli algoritmi validati nella nuova architettura; non è necessario riscrivere inutilmente librerie affidabili. Non modificare coefficienti o inventare la metodologia per poter dichiarare il tool completo. L’assenza del sorgente del calcolo non deve interrompere lo sviluppo degli altri ambiti, ma il motore resta un requisito da completare dopo aver ottenuto la fonte mancante.

In caso di conflitto con espressioni del documento come “conservare il tool” o “lavorare sul repository mantenuto”, prevale qui la richiesta di un nuovo prodotto autonomo e completo; resta l’obbligo di non cancellare codice e dati esistenti. Non effettuare una migrazione su dati reali né pubblicare in produzione con questo incarico.

### 1. Fonti, perimetro e precedenze

- Fonte funzionale: `HSE_SPEC_CODEX.md`; l'edizione Word 1.2 contiene gli stessi requisiti. Le sezioni RF-57–RF-76 aggiornano e integrano le precedenti in caso di conflitto.
- Il prodotto comprende Risk Index, valutazioni, storico, sinottici impresa con importazione immagini assistita, calendario analitico, esportazioni management e i quattro nuovi moduli descritti sotto.
- Il lavoro deve essere un supporto all'HSE: niente campi ripetuti, nessun modulo obbligatorio per accedere agli altri, dati riutilizzati tramite collegamenti. Mostra prima i campi essenziali e rendi i dettagli integrabili.
- Non aggiungere modifiche al modello di rischio proposte e rifiutate nella conversazione. Pesi, soglie, detection e bonus devono essere quelli del modello vigente verificato nel sorgente.
- Non inventare formule mancanti. Se non sono disponibili sorgenti sufficienti, completa i moduli indipendenti; identifica come bloccata la sola funzione di calcolo non verificabile, indicando la fonte necessaria. Non usare il vecchio modello di luglio per colmare lacune del modello 2.0.0.
- Le proposte tecniche della specifica sono scelte predefinite di implementazione: risolvi autonomamente le scelte reversibili, documentando i compromessi. Chiedi solo informazioni realmente indispensabili e continua nel frattempo le parti indipendenti.

### 2. Piattaforma e integrazione

La soluzione di riferimento è un plugin WordPress autonomo denominato `hse-risk-platform`, in PHP e JavaScript, con archivio tramite WordPress/MySQL. AlterVista è un possibile hosting; Elementor è un'integrazione visuale facoltativa, non il backend applicativo.

Esponi l'applicazione con lo shortcode `[hse_platform]`, utilizzabile in una pagina WordPress e nel widget Shortcode di Elementor. Se utile, aggiungi un widget Elementor dedicato che richiami la stessa UI. Il plugin deve funzionare senza Elementor e senza Elementor Pro. Non mettere il codice gestionale in `functions.php`, in un widget HTML o in un iframe che continui a dipendere dalla vecchia app.

Ispeziona prima il repository e le capacità effettive del piano hosting. Verifica PHP, estensioni ZIP/XML/immagini, database, upload, memoria, tempi, HTTPS, cache e possibilità di installare plugin. Se il piano non è accessibile, produci un ambiente locale verificabile e una checklist di compatibilità; non dichiarare verificato AlterVista senza evidenza.

Non richiedere Python/Tesseract/Node come processi permanenti sul server. Build frontend e dipendenze devono essere incluse nello ZIP installabile. L'OCR può usare un worker nel browser e dati linguistici italiani, o un adattatore compatibile esplicitamente configurato; in ogni caso deve rispettare il riconoscimento strutturale della tabella e la revisione assistita, non soltanto restituire testo libero.

Usa documentazione ufficiale aggiornata di WordPress, Elementor, hosting e librerie prima di fissare versioni e dipendenze. Evita servizi a pagamento e credenziali esterne obbligatorie non richieste. Se una capacità non è disponibile, implementa e documenta un comportamento degradato esplicito, senza simulare il successo.

### 3. Dettaglio dei quattro moduli aggiuntivi, oltre a tutte le funzioni base

**A. Sopralluogo rapido da smartphone — RF-60–RF-62**

Cantiere già selezionato, area facoltativa o da specificare, nota e foto. Un appunto non deve richiedere una checklist completa. Salva, riapri, modifica e collega l'osservazione a riunione, documenti o bozza di segnalazione senza ricopiare i dati. Mantieni originali delle foto e annotazioni separate. Retry idempotente. Nessun effetto automatico sul Risk Index e nessuna registrazione implicita in HSEQ4ALL.

**B. Preparazione riunione — RF-63–RF-65**

Da cantiere e settimana prepara un ordine del giorno usando sinottici confermati, compresenze da verificare e osservazioni selezionate. L'utente sceglie e riordina gli argomenti, annota decisioni e azioni, finalizza e scarica Word/PDF. Conserva lo snapshot delle fonti; una modifica successiva del calendario non riscrive il verbale finalizzato. Non inventare partecipanti o firme e non inviare comunicazioni automaticamente.

**C. Toolbox dalle attività — RF-66–RF-68**

Prepara tracce brevi pertinenti a lavorazioni, area e condizioni dichiarate mediante modelli revisionati e abbinamenti espliciti. L'utente rivede e personalizza. Mostra riferimenti documentali solo se effettivamente disponibili. Separa il materiale preparato dall'incontro effettivamente svolto: download e generazione non producono sensibilizzazioni o bonus. Riutilizzo nella valutazione mensile solo tramite collegamento e regole già esistenti.

**D. Documenti per area e mappa KMZ — RF-69–RF-73**

Collega documenti o URL a WTG/aree tramite ID stabili, categorie e revisioni; uno stesso documento può riguardare più aree. Importa KMZ/KML in anteprima e normalizza le geometrie compatibili in GeoJSON WGS84. Classificazione e conferma da parte dell'utente: una linea di cavidotto non diventa una strada.

Genera una vista tecnica 2D sempre disponibile su sfondo neutro, anche senza servizi cartografici. Il KMZ può non contenere alcuna fotografia: non promettere immagini satellitari ricostruite dal solo tracciato. Basemap e overlay solo se disponibili, georeferenziati e con condizioni compatibili con uso ed esportazione. Segnala gli elementi non supportati. Non seguire automaticamente NetworkLink o URL inclusi nei documenti importati.

Permetti di aggiungere segnali e annotazioni con clic/tocco, spostamento, rotazione, etichetta, note, stato e collegamento a documenti. Conserva coordinate e revisioni, non soltanto un'immagine. Offri alternativa al drag. Export PNG/PDF A3/A4 con legenda, data e revisione; scala/nord corretti quando applicabili; sorgenti strutturate salvabili e ricaricabili. Non qualificare simboli personalizzati come conformi a una norma senza catalogo verificato.

### 4. Design, accessibilità e semplicità

Applica sfondo #F3F4F6, superfici bianche, testo #20252B, navigazione #252A31, arancio scuro #A63D00 per azioni con testo bianco e inserti #F97316 con testo scuro. Distingui l'arancione di interazione dagli stati di allarme. Usa token CSS e componenti riutilizzabili; evita stili globali che alterino WordPress o Elementor.

Sviluppa prima il percorso mobile, poi tablet e desktop. Agenda su smartphone, viste settimanali/matrice sul desktop. Niente sette colonne compresse sul telefono, comandi solo hover o campi nascosti dalla tastiera. Obiettivo WCAG 2.2 AA con evidenze di verifica: tastiera, focus, contrasto, etichette, messaggi, zoom, orientamento e reflow. Una palette o un punteggio automatico non costituiscono certificazione.

Gli export management devono essere documenti aziendali progettati: sintesi, driver, trend comparabili, priorità e decisioni; PPTX 16:9 modificabile e PDF corrispondente. Conserva report operativi completi separati e verifica visivamente i file finali. Non usare screenshot come unica presentazione e non comprimere tabelle fino a renderle illeggibili.

### 5. Dati e accessi

Implementa RF-74 con ID stabili, collegamenti fra moduli, versioni concorrenti, snapshot e migrazioni. Auth WordPress, capability e autorizzazione per cantiere/impresa su ogni endpoint e download. Un nonce non sostituisce i permessi. Gli allegati riservati non devono essere raggiungibili pubblicamente tramite URL diretto della media library.

Valida e sanifica input, esegui escaping e usa query preparate. Limita ZIP/KMZ decompressi, blocca path traversal, XML con entità esterne e contenuti attivi. Non esporre segreti nel browser. Non cancellare automaticamente dati in aggiornamento o disinstallazione. Gestisci conflitti di revisione e retry senza duplicati.

### 6. Metodo di lavoro e consegna

1. Leggi l'intera specifica, ispeziona repository e ambiente e registra la matrice `requisito → file/componente → test → stato` in `IMPLEMENTATION_STATUS.md`.
2. Definisci un piano breve e inizia l'implementazione. Usa RF-75 per organizzare il lavoro, sviluppando tutti gli ambiti della sezione 0 e completando percorsi end-to-end funzionanti. Non presumere esistenti backend o funzioni precedenti.
3. Predisponi dati demo sintetici chiaramente riconoscibili, incluso KMZ di prova. Non usare dati demo per far apparire completate integrazioni non funzionanti.
4. Esegui test dei flussi RF/AT, isolamento tra cantieri, persistenza, conflitti e importazioni non valide. Testa le larghezze 320/375/768/1024/1440 CSS px e verifica i file esportati. Distingui ciò che hai realmente eseguito dalle verifiche solo predisposte.
5. Consegna codice, plugin ZIP installabile, README per WordPress/AlterVista/Elementor, migrazioni, dipendenze/licenze, test e istruzioni di backup/ripristino. Il sito non deve richiedere l'avvio di strumenti sul computer dello sviluppatore.
6. Riporta completamenti, limiti reali e impedimenti puntuali con riferimento ai requisiti; non segnare completato un requisito che ha soltanto un pulsante o una UI senza persistenza.

Questa istruzione autorizza preparazione, sviluppo e test del pacchetto. Non pubblicare sul sito di produzione, sostituire database o migrare dati reali nell'ambito di questo prompt. Prepara il risultato installabile e la procedura concreta di rilascio.

Inizia ora dalla lettura completa di `HSE_SPEC_CODEX.md` e dall'ispezione del progetto, poi prosegui con lo sviluppo completo da zero fino alla consegna del tool installabile e verificato.
