# Evidenze di verifica — 20 ottobre 2026, plugin 0.2.1

Runtime locale: WordPress 7.1.3, PHP 8.0.30, MariaDB 11.4.13, Chromium, Node 24.19.0. Dati sintetici riconoscibili, nessuna migrazione reale o pubblicazione in produzione. Evidenze generate in `tests/artifacts` (escluse da Git).

## Test riproducibili

- `npm run build`: bundle, worker/WASM/OCR italiano, font e licenze inclusi; nessun processo Node/Python sul sito.
- `npm run test:model`: 357 confronti con le funzioni Python originali estratte dal DOCX; componenti, bonus, soglie, contesto, detection descrittiva, ragioni di pertinenza, riconciliazione e 2.142 scenari indipendenti. Confini esatti e valori immediatamente successivi per tutte le fasce. Il confronto non è una validazione predittiva del modello.
- `npm run test:integration`: 56 controlli su WordPress REST/MySQL reali. Calcolo temporaneo e salvataggio esplicito, input/politica modificati rifiutati, idempotenza anche dopo cambio politica, scenari senza modifica dello storico, export temporaneo e conservazione di Saved durante nuove bozze. Soglie 61/81, contesto con priorità ore, contributi riconciliati, cataloghi sconosciuti rifiutati. Accessi per cantiere/impresa/lettore/anonimo anche sui nuovi endpoint. Persistenza, conflitti, backup/ripristino, migrazione ripetibile, 10 imprese/100 attività, riunione e azione unica, toolbox/incontri separati, KML/KMZ, stili locali, file ostili rifiutati e allegati senza URL pubblico. Test Europe/Rome su confine mese e cambio ora.
- `npm run test:browser`: login reale, anagrafica, collegamenti archivio, calendario a 320/375/768/1024/1440 px, persistenza dopo reload, export dei sei formati, ICS, tavole PNG e PDF A3/A4.
- `npm run test:ocr`: worker italiano locale, due righe con preposti/POS/operatori associati; prospettiva identità. Aggiunti casi con celle multilinea, otto date reali e correzioni mantenute dopo riestrazione. È un campione sintetico, non dimostra 95% su sinottici reali.
- `npm run test:workflows`: due foto persistenti, annotazioni separate dagli originali ed export delle evidenze; 25 combinazioni modulo/larghezza con axe e controllo reflow.
- `npm run test:risk-browser`: calcolo, modifica e blocco del salvataggio, ricalcolo, inserimento, scenari, storico/confronto, persistenza dopo reload, cinque larghezze con axe, export numerici e sinottico di 100 attività.
- `npm run test:meeting`: verbale con foto private collegate tramite snapshot, download Word/PDF e verifica delle immagini incorporate.
- `python tests/validate_exports.py`: apertura PDF/Word/Excel e XML PPTX, indici Excel uguali al risultato salvato, grafico PowerPoint nativo editabile, stesso numero di pagine nel PDF management corrispondente, sinottico A3 multipagina e Word con tutte le 100 righe, intestazioni ripetute e foto nei report. Il grafico Excel è raster, con valori numerici disponibili nei fogli.
- `npm run test:navigation`: menu mobile azionabile da tastiera, navigazione desktop e input conservati in verticale/orizzontale, tre ulteriori controlli axe.
- Ispezione visiva di sintesi management, grafico contributi e sinottico A3 renderizzati; 100 attività su 17 pagine nel caso lungo. Corretto un ancoraggio OOXML di ExcelJS: il grafico è ora leggibile anche da openpyxl.
- PHP lint su tutti gli otto file. Installazione dallo ZIP in WordPress isolato: `bash tools/test-package.sh` con l’installer WordPress su PHP 8.0.30, shortcode protetto e autenticato, calcolo Wind/Solar/BESS e conservazione dei dati dopo riattivazione, senza Elementor.

`npm test` esegue gli otto gruppi principali in sequenza, fermandosi al primo errore. `tools/test-integration.sh` conserva gli artefatti precedenti in `/tmp`, rigenera solo dati sintetici e conserva i container. Non usare questi strumenti con database di produzione.

## Limiti e gate reali

- AlterVista effettivo non accessibile: plugin personalizzati, PHP/estensioni, HTTPS, cache, upload/memoria e storage vanno provati sul piano scelto. La prova locale non certifica l'hosting.
- Widget Elementor implementato sullo stesso shortcode. Download ufficiale del plugin Elementor tentato, bloccato dal proxy HTTP 403: integrazione reale non verificata. Il pacchetto funziona senza Elementor.
- Non disponibili 20 sinottici rappresentativi con trascrizione manuale, cinque utilizzatori e dispositivi iOS/Android fisici. Nessuna accuratezza OCR o tempo di usabilità viene inventato.
- Axe/reflow automatizzati non certificano WCAG 2.2 AA. Restano audit manuale completo, lettore di schermo, tutti gli stati, tastiera a schermo e revisione accessibilità dei file in Office/PDF.
- Diagnostica immagine e raggruppamento tabellare sono assistiti: layout non riconosciuti richiedono mapping/controllo esplicito, mai valori inventati. Overlay georeferenziati e icone cartografiche remote sono esclusi con avviso; tavola vettoriale disponibile. Scala omessa, nessuna conformità normativa dei simboli personalizzati.
- Modelli toolbox provenienti dal precedente codice, da adattare e revisionare con l'HSE; non sono autorizzazioni al lavoro o prescrizioni estratte da POS non disponibili.

La matrice `IMPLEMENTATION_STATUS.md` mantiene Parziale per requisiti che richiedono tali verifiche esterne. Nessun blocco per sorgente del motore mancante: il modello è ora disponibile e verificato contro la fonte consegnata.

## Collaudo aggiuntivo 0.2.1 sul PHP dell’hosting

Suite `npm test` completa superata con `HSE_TEST_CONTAINER=hse-wp-php80 HSE_EXPECT_PHP=8.0.30 HSE_TEST_URL=http://127.0.0.1:8084`: tutti gli otto gruppi; poi validazione degli export superata. Controlli parser/API e test negativo ZIP superati separatamente. PHP e dipendenze non sono dedotti dall’immagine PHP 8.3: il runtime riporta davvero 8.0.30 anche dalle chiamate HTTP.

Installazione su nuovo WordPress/database con prefisso `avtest_`: la vecchia 0.2.0 è rifiutata dall’installer per `incompatible_php_required_version`; la 0.2.1 è installata/attivata, quattro tabelle InnoDB create e dati conservati dopo riattivazione. Verificati anche amministrazione WordPress, login e REST HTTP in sottocartella. L’installer usato è il `Plugin_Upgrader` di WordPress; non una semplice estrazione del file ZIP.

Sono rimasti invariati byte per byte motore/cataloghi e bundle JavaScript. Gli otto file sono parsati e le 107 funzioni globali verificate con il bootstrap WordPress corretto. Dettagli: PHP80_COMPATIBILITY.md.

L’ambiente offline genera avvisi dei controlli aggiornamenti WordPress.org bloccati dalla rete/configurazione del test; non sono errori del motore o degli endpoint del plugin. Servizi di aggiornamento esterni, hosting AlterVista reale e gli altri gate della checklist non sono stati certificati.

Il pacchetto finale 0.2.1 è stato anche caricato/sostituito dall’amministrazione WordPress via browser su PHP 8.0.30: esito positivo, plugin attivo e REST funzionante dopo il caricamento. Hash e dimensione finali sono nel QA_RESULTS.json del repository.
