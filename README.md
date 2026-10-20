# HSE Risk Platform

Plugin WordPress autonomo, specifica 1.2 del 19/10/2026. Versione **0.2.0**, con motore PHP **2.0.0** portato dal codice completo allegato, senza ricostruire coefficienti dai massimali. Calcolo, salvataggio esplicito, storico, confronti e scenari sono collegati ai moduli operativi esistenti. Le verifiche esterne e i limiti residui sono distinti nella matrice; la Definition of Done complessiva richiede anche i collaudi reali indicati sotto.

## Installazione WordPress / AlterVista

1. In staging, eseguire backup completo di database e file WordPress.
2. Verificare che il piano permetta plugin personalizzati. Requisiti: WordPress ≥6.6, PHP ≥8.1, MySQL/MariaDB con InnoDB, estensioni mysqli, JSON, fileinfo, mbstring, XML/SimpleXML e ZIP; GD consigliata. Verificati localmente WordPress 7.1.3, PHP 8.3.35 e MariaDB 11.4.
3. Consigliati PHP memory_limit ≥256 MB e upload/post_max_size sufficienti per lo ZIP e file da 15 MB. Il browser deve supportare WebAssembly, worker e JavaScript moderno. I generatori e l'OCR sono inclusi: non occorrono Composer, Node, Python, Tesseract installato sul sito o API a pagamento.
4. Caricare `dist/hse-risk-platform-0.1.0.zip` da **Plugin → Aggiungi plugin → Carica plugin**, installare e attivare. Se il limite upload è inferiore allo ZIP, estrarre la cartella `hse-risk-platform` in `wp-content/plugins` tramite il gestore file/FTP del proprio piano; non modificare functions.php.
5. Creare una pagina con il blocco Shortcode: `[hse_platform]`. In Elementor usare il widget **Shortcode** con lo stesso testo. È disponibile anche il widget HSE Risk Platform, quando Elementor è attivo. Elementor e Elementor Pro non sono necessari; il plugin non usa iframe o la vecchia app.
6. Accedere come amministratore WordPress. Creare cantiere Wind/Solar/BESS, poi **Archivio e impostazioni → Aree / WTG**, **Imprese**, **Assegnazioni**. Creare prima gli account nominativi in **Utenti** WordPress; inserire ID utente, ruolo e cantiere. Per HSE impresa assegnare anche l'impresa e l'eventuale condivisione dei piani.
7. Verificare accesso da un secondo account/sessione. Escludere pagina HSE e `/hse/v1/*` da cache di hosting/plugin/CDN; escludere gli URL REST con `rest_route` se i permalink sono semplici. Il plugin invia no-store/noindex, ma configurazioni di cache esterne vanno provate.
8. Verificare HTTPS, dimensioni upload, worker/WASM e download sul piano effettivo prima di usare dati reali. Nessuna pubblicazione o migrazione di dati reali è stata eseguita.

**AlterVista non è stato verificato sul piano reale**. Mancano accesso all'hosting, informazioni del piano e prove con la sua cache. Usare [docs/RELEASE_CHECKLIST.md](docs/RELEASE_CHECKLIST.md); non interpretare il funzionamento locale come certificazione di compatibilità del piano.

## Uso dei moduli

- **Sopralluogo rapido**: cantiere selezionato, nota o foto, area facoltativa, Salva. Riapertura/revisioni, posizione soltanto su richiesta, annotazioni come copie distinte. Porta in riunione o prepara una segnalazione collegata senza duplicare l'originale.
- **Sinottici**: impresa e lunedì della settimana, attività/aree/preposti/POS, date e operatori, forza lavoro giornaliera dichiarata. L'importazione di immagini/PDF/testo produce una bozza: rivedere i campi e poi **Conferma e inserisci nel calendario**. Motivare le discrepanze nei totali senza sommare arbitrariamente persone duplicate.
- **Calendario**: agenda mobile, elenco, matrice Area × Giorno e panoramica per date; filtri, ricerca, condizioni, compresenze da verificare e ICS. Pubblicazione e autorizzazione al lavoro sono distinte.
- **Riunioni**: prepara da settimana e sopralluoghi selezionati, escludi/riordina argomenti, registra partecipanti dichiarati, decisioni, responsabili e scadenze. Finalizza esplicitamente; le fonti restano uno snapshot. Non invia convocazioni e non firma documenti.
- **Toolbox**: seleziona attività confermate/documenti disponibili oppure inserisci lavorazione, personalizza la traccia locale. **Registra incontro svolto** è un'operazione distinta. Download e generazione non creano incontri né bonus.
- **Documenti / mappa**: documenti con revisioni e più aree; importazione KML/KMZ con anteprima, classificazione esplicita e associazione tramite ID. Segnali personalizzati, coordinate/orientamento modificabili, modalità modifica, undo, zoom, PNG/PDF A3/A4, backup strutturato e KML. NetworkLink e overlay non supportati non vengono caricati.
- **Valutazioni**: bozze, quattro passaggi e validazioni. **Calcola / Ricalcola** produce un risultato temporaneo; solo **Salva e inserisci** alimenta lo storico. Input modificati richiedono nuovo calcolo. Sintesi, contributi, riconciliazione, soglie, contesto e sei scenari indipendenti; storico con mesi mancanti distinti da zero e confronti omogenei. Target comune in Archivio, configurabile solo dall’amministratore. Contratto e provenienza in [docs/MODEL_2_0_0.md](docs/MODEL_2_0_0.md); modifiche e compatibilità in [docs/CHANGELOG.md](docs/CHANGELOG.md).
- **Advisor / checklist / Action Plan**: proposte qualitative collegate a segnalazioni reali; nessuna causa tecnica accertata o misura normativa inventata. Checklist modificabili e azioni persistenti con evidenza di chiusura.

## Importazione e qualità

OCR italiano e testo PDF vengono elaborati nel browser senza inviare documenti a servizi esterni. Rotazione, ritaglio e prospettiva a quattro vertici; mapping esplicito delle colonne, rilevamento griglie e confini di riga modificabili per celle multilinea, otto o più date esplicite senza compressione, originali/riquadri sorgente, revisore Fonte/Dati con zoom, selezione righe e conservazione delle correzioni alla riestrazione. Limiti iniziali: 15 MB, 5 pagine, 20 megapixel/pagina. Celle unite, righe multilinea complesse e foto difficili richiedono revisione manuale. **Non è stata raggiunta o dichiarata la soglia del 95% su 20 sinottici reali**: il campione rappresentativo non è stato fornito.

Le immagini sorgente OCR sono temporanee nella sessione finché l'utente non sceglie esplicitamente un upload come allegato. Le copie annotate non modificano gli originali. Originali e revisioni sono conservati senza scadenza automatica nel database; eventuale rimozione amministrativa richiede una procedura di conservazione e backup separata. Non è promesso funzionamento offline. I file riservati sono nel database, scaricabili solo dopo autorizzazione, senza URL pubblici di media library.

## Export e backup

Word, Excel, PDF, PPTX modificabile 16:9, sintesi management PDF, ICS, JSON, tavole PNG/PDF e KML sono generati nel browser; gli export di record salvati registrano uno snapshot autorizzato con revisione/fonte. Le valutazioni esportano gli stessi indici/contributi/soglie dello snapshot; PPTX con grafico nativo modificabile e PDF corrispondente. Sinottico A3 tabellare multipagina con intestazioni ripetute, Word con tabelle, verbali con decisioni/azioni e foto selezionate. Il grafico Excel è un’immagine, con dati numerici nei fogli dedicati. Rimane il collaudo editoriale/accessibilità in Office e sui documenti reali.

**Backup JSON distinti**: valutazioni, sinottici, moduli operativi. Comprendono allegati referenziati, schema e ID. Il ripristino richiede il cantiere originale, anteprima e conferma, è atomico e crea nuove revisioni; i piani ripristinati vanno riesaminati prima di pubblicarli. Non sostituisce il backup completo database, necessario per utenti, assegnazioni e intera cronologia.

**Backup completo**: usare gli strumenti dell'hosting per esportare il database WordPress e copiare plugin/configurazione/file del sito. Le quattro tabelle del plugin contengono anche gli originali riservati: includerle integralmente, custodire il dump e provare il ripristino su staging. Aggiornamento, disattivazione e uninstall non cancellano automaticamente dati. Non importare un dump sul database di produzione senza procedura separata autorizzata.

## Sviluppo e verifiche

Nel cloud:

```bash
cd /workspace/hse-risk-platform
npm --cache /workspace/.npm-cache ci
npm run build
bash tools/dev-up.sh
npm test
python tests/validate_exports.py
python tools/package.py
```

Docker è usato solo per WordPress/MySQL di sviluppo. I container `hse-wp` e `hse-db` sono locali, con database sintetico isolato e credenziali di test generate nel bootstrap; non usarli in produzione. Chromium deve essere disponibile in `/usr/bin/chromium` per i test browser. `tools/dev-up.sh` è ripetibile e conserva i container esistenti. La produzione usa soltanto il plugin compilato.

Evidenze e limiti: [docs/QA.md](docs/QA.md), [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md). Dati sintetici in `fixtures/`, incluso KMZ con 7 WTG, strada, cavidotto e poligono. Nessuna fonte normativa ufficiale o logo è dedotto dai dati demo.

Licenza applicazione GPL-2.0-or-later. Dipendenze versionate in package-lock.json e relative licenze in `hse-risk-platform/THIRD_PARTY_LICENSES.txt`.
