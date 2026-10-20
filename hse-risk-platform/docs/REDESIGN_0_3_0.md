# Redesign 0.3.0 — 20 ottobre 2026

## Implementazione e confini

Frontend JavaScript vanilla con schemi condivisi e bundle esbuild; backend PHP WordPress REST con quattro tabelle InnoDB. Nessuna nuova dipendenza. Il design system CSS è isolato sotto `.hse-platform`: navy, blu e teal, componenti uniformi, spaziatura, gerarchia, feedback, focus e responsive. Dashboard con tre tecnologie, percorso iniziale, contatori dei soli record accessibili, elenco cantieri e accessi coerenti con i permessi. Wizard esistente completato con progressione e Avanti/Indietro; sintesi Risk Index, driver e formati di export evidenziati. Schermate operative, calendario, mappe, storico e archivi usano gli stessi componenti.

I ruoli restano quelli esistenti: amministratore WordPress, referente HSE `manager`, lettore `reader`, Impresa `company`. Nessuna nuova autorizzazione o ruolo “Enel” inventato. NC formali HSEQ4ALL e NC informali fanno riferimento allo stesso periodo; il tooltip detection mantiene la descrizione effettiva del modello. Formule, soglie, coefficienti, cataloghi, detection, schema 1, API, autenticazione e generatori di export sono invariati rispetto a 0.2.1. La gestione delle risposte asincrone evita che una schermata precedente ricompaia sopra il modulo aperto.

## Asset

`assets/images/wind.svg`, `solar.svg`, `bess.svg`: illustrazioni vettoriali originali create per questo progetto, distribuite con la licenza del plugin. Parco eolico, impianto fotovoltaico e container batterie, senza loghi ufficiali. Nessun asset precedente utilizzabile era presente nella cartella grafica. File locali, dimensioni dichiarate, testi alternativi, lazy loading e decoding asincrono; nessuna richiesta a font o immagini esterni.

## WordPress / AlterVista

Template selezionabile **HSE Platform · applicazione a pagina intera**, registrato dalle API WordPress. Mantiene `wp_head`, `wp_body_open`, `wp_footer`, autenticazione e shortcode `[hse_platform]`. Non carica i template header/sidebar/footer del tema; gli stili della cornice si applicano solo al template selezionato. Il layout incorporato continua a funzionare nel template del tema. Nessuna impostazione tema, homepage o dato produttivo viene cambiata dal plugin.

Su AlterVista: backup file/database, aggiornare prima in staging, poi **Pagine → pagina HSE → Modifica → Template → HSE Platform · applicazione a pagina intera**. Se serve come homepage: **Impostazioni → Lettura → Una pagina statica**. Nessun cambio di tema René necessario. Rollback: ZIP 0.2.1 e template precedente, senza eliminare il plugin; proteggere le modifiche successive prima di qualsiasi ripristino database.

La richiesta HTTPS al sito pubblico `hseriskindex.altervista.org` è stata bloccata dal proxy dell’ambiente: `curl: (56) CONNECT tunnel failed, response 403`. Non è stata ispezionata l’installazione René reale né usata l’amministrazione remota. Nessuna modifica o pubblicazione sul sito di produzione.

## Collaudo

Suite completa superata su PHP **8.0.30**, WordPress **7.1.3**, MariaDB **11.4.13**: nove gruppi npm, 357 confronti Python/PHP, 2.142 scenari indipendenti, 56 controlli backend, export verificati e 13 controlli aggiuntivi redesign senza violazioni axe o overflow. Le prove automatiche complessive coprono 51 combinazioni pagina/viewport con axe. Parser/API verificati su 9 file PHP e 119 funzioni; attivazione senza ZIP bloccata con messaggio esplicito. Motore, API, schema, cataloghi ed export sorgenti confrontati con 0.2.1 e invariati.

Gli esiti finali dello ZIP esatto vengono registrati in `REDESIGN_QA.json`; i test sono riproducibili con:

```sh
HSE_TEST_CONTAINER=hse-wp-php80 HSE_EXPECT_PHP=8.0.30 HSE_TEST_URL=http://127.0.0.1:8084 npm test
python tests/validate_exports.py
bash tools/php80/test-package.sh
HSE_TEST_PACKAGE_FILE="$PWD/dist/hse-risk-platform-0.3.0.zip" node tests/php80-web.mjs
```

La suite include confronto modello Python/PHP, REST/DB, separazione utenti, persistenza, NC/ispezioni/detection, scenari, storico, foto, OCR e formati di export; test browser su form, risultati, calendario, navigazione e tre ruoli effettivi oltre all’amministratore. Il test redesign prepara solo utenti e dati sintetici locali. Prove da 320 a 1920 px, ingrandimento del testo al 200%, tastiera nel menu/wizard/aiuti, verifiche axe WCAG 2.2 AA e controllo degli errori JavaScript. Non è una certificazione WCAG.

Durante il collaudo sono state corrette sovrapposizioni asincrone e il contrasto del pulsante in attività. Il test di creazione ha portato a separare etichetta e select, mantenendo associazione esplicita `for`/`id`. Un errore di WordPress `user-profile.min.js` durante l’abbandono immediato del profilo è stato isolato nel percorso del test: il login ora usa il normale `redirect_to` alla pagina HSE, come il link del plugin. Nessun file core modificato e nessun errore applicativo viene filtrato.

## Verifiche esterne ancora necessarie

Tema René e personalizzazioni/Elementor dell’installazione reale; versione WordPress, estensioni, permessi CREATE/ALTER e InnoDB, HTTPS, cache autenticata e REST, worker/WASM, timeout, upload e spazio database del piano AlterVista. Rimangono i collaudi con screen reader e dispositivi iOS/Android reali, utenti rappresentativi e documenti Office/PDF finali: i test automatici non li sostituiscono. Restano validi i gate in `RELEASE_CHECKLIST.md`, inclusi 20 sinottici rappresentativi.

Requisiti invariati: WordPress ≥6.6, PHP ≥8.0.30, mysqli/mbstring/fileinfo/SimpleXML/ZIP. Consigliati 256 MB PHP, upload 32 MB/post 48 MB per ZIP circa 21 MB, pacchetto DB adeguato agli allegati fino a 15 MB. GD resta facoltativa per il plugin. Le prove locali non certificano questi limiti sull’hosting.
