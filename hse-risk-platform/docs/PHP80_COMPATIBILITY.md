# Verifica PHP 8.0.30 — HSE Risk Platform 0.2.1

## Problema e modifica

La 0.2.0 dichiarava PHP minimo 8.1. L’installer WordPress su PHP 8.0.30 la rifiuta con `incompatible_php_required_version`: il problema riportato è stato riprodotto sul runtime esatto. La 0.2.1 dichiara PHP 8.0.30 e verifica le estensioni prima della migrazione.

Il controllo del codice non ha trovato una necessità di PHP 8.1: gli otto file passano il parser PHP 8.0.30; tutte le 107 funzioni globali sono disponibili con WordPress e gli include file.php/upgrade.php realmente usati. Funzioni stringa `str_contains`/`str_starts_with`, arrow function e proprietà tipizzate sono già supportate. Non sono presenti enum, proprietà readonly, tipi intersezione o dipendenze Composer che richiedano 8.1. Sono stati controllati ZipArchive, finfo, SimpleXMLElement e DateTimeZone. Le librerie OCR/PDF/DOCX/XLSX/PPTX sono JavaScript: bundle e risorse non sono stati ricompilati né sostituiti.

Non si introducono coefficienti o approssimazioni: `includes/risk.php`, cataloghi e modello 2.0.0 sono invariati rispetto alla 0.2.0.

## Ambiente effettivo

- PHP **8.0.30**, immagine ufficiale apache con digest `sha256:c87b4c94d53b35520467b6d026f38656ab9a6d446fa3a0fbba1bc633125f9ad2`; versione controllata da CLI e da richieste HTTP all’API del plugin.
- WordPress **7.1.3**, MariaDB **11.4.13**, quattro tabelle **InnoDB**. Un secondo sito/database nuovo, installato in sottocartella, usa il prefisso `avtest_`.
- PHP mysqli, mbstring, fileinfo, SimpleXML e ZIP effettivamente disponibili; PHP memory_limit 256M, upload 32M/post 48M. GD non installata: le operazioni foto/export del plugin sono riuscite comunque nel browser.
- Database e utenti sintetici. Nessun accesso, cambio PHP o installazione sul sito AlterVista di produzione.

Il driver Docker VFS duplicava i filesystem e saturava il disco nelle build. Il runtime è stato predisposto direttamente nel container PHP ufficiale, compilando mysqli/ZIP con il suo sorgente 8.0.30 e pacchetti Debian scaricati via HTTPS/verificati SHA-256. Nessun modulo PHP di un’altra versione è stato riutilizzato. Il codice WordPress proviene dall’immagine ufficiale già presente; il PHP 8.3 dell’immagine sorgente non viene eseguito nei test PHP 8.0.30. Script riproducibile: `tools/php80/prepare.sh`.

## Verifiche eseguite

- `tests/php80-compat.php`: parsing di 8 file, risoluzione di 107 funzioni, classi/estensioni, `validate_plugin_requirements` e quattro tabelle InnoDB.
- `tests/model_parity.py`: 357 casi Python/PHP, 2.142 scenari originali, fasce e riconciliazione sul PHP esatto.
- `tests/integration.php`: 56 controlli REST/MySQL su dati, permessi, conflitti/retry, calcolo/salvataggio/storico/scenari, calendario, riunioni, toolbox, file privati, KML/KMZ e backup/ripristino; più date Europe/Rome.
- Browser: login effettivo, cinque larghezze, salvataggi/reload, foto e copie annotate, meeting, calendario, OCR italiano locale, celle multilinea/otto date e correzioni conservate, risultati/export numerici; menu da tastiera e input mantenuti al cambio orientamento. L’attesa dell’inizializzazione è esplicita nel test tastiera.
- Export aperti e controllati come nelle altre evidenze QA: PDF/Word/Excel/PowerPoint, grafico PPTX modificabile, dati Excel coerenti, A3 con 100 attività, ICS ed evidenze fotografiche.
- `tests/php80-install.php`: installer reale `Plugin_Upgrader` WordPress. Riprodotto il rifiuto della 0.2.0; la 0.2.1 viene installata e attivata su database nuovo, con zero tabelle plugin prima e quattro InnoDB dopo. Verificati prefisso non standard, Wind/Solar/BESS e dati conservati dopo disattivazione/riattivazione.
- `tests/php80-web.mjs`: dal server web PHP 8.0.30, accesso WordPress, shortcode, API autenticata con creazione/modifica e plugin attivo versione 0.2.1 nell’amministrazione; installazione in sottocartella.
- `tests/php80-missing-zip.php`: con la sola ZIP disabilitata, attivazione bloccata con messaggio esplicito e registrazioni invariate.

Gli artefatti locali sono in `tests/artifacts`; il riepilogo verifiche è in `docs/QA_RESULTS.json`. Non sono un audit di sicurezza o una certificazione WCAG.

## Requisiti del piano ancora da verificare

Dell’hosting effettivo è nota la versione PHP 8.0.30 comunicata dall’utente. Non sono stati verificati da remoto WordPress ≥6.6, estensioni/permessi del database, InnoDB, memoria/upload/post, max_allowed_packet/spazio per gli allegati grandi, HTTPS, cache, worker/WASM e timeout. Per un ZIP di circa 21 MB servono limiti adeguati (upload 32 MB/post 48 MB consigliati); in alternativa usare gestore file/FTP se consentito e poi attivare da WordPress. I test non attestano tutti i caricamenti al limite massimo sul piano reale.

Restano anche i precedenti collaudi esterni: Elementor reale, iOS/Android fisici, 20 sinottici rappresentativi, cinque utilizzatori e audit manuali di accessibilità/file Office. Il downgrade del requisito dichiarato non risolve né certifica automaticamente questi gate.

## Verifica del pacchetto finale dopo confezionamento

Il file `dist/hse-risk-platform-0.2.1.zip` è stato caricato e sostituito dall’amministrazione WordPress via HTTP su PHP 8.0.30, poi verificato attivo con login, shortcode e creazione/modifica REST. SHA-256: `cd8a6b31ca896a6e2c3813d4820a7cde236d6de097c5ba5654771cee9b1e90e7`. Questa evidenza successiva al confezionamento è registrata nel repository; non richiede di ricompilare il bundle o modificare il pacchetto verificato.
