# Architettura e contratti

Plugin autonomo PHP 8.1+/WordPress, frontend JavaScript compilato con esbuild. Nessun processo Node/Python/Tesseract richiesto sul sito. Elementor usa lo shortcode WordPress; nessuna dipendenza da Elementor Pro, Streamlit o servizi AI. Tutti i percorsi operativi usano MySQL, non localStorage.

## Persistenza e migrazioni

`includes/store.php`: schema 1 con quattro tabelle InnoDB tramite `dbDelta`, prefisso WordPress rispettato:

- `hse_records`: UUID, tipo, cantiere/impresa, versione, autore, timestamp UTC, contenuto JSON.
- `hse_revisions`: snapshot immutabili delle revisioni, autore della modifica; unico record/versione.
- `hse_requests`: chiave utente/request_id, fingerprint e risposta per retry idempotenti.
- `hse_assets`: file binari riservati, hash SHA-256 e perimetro. Nessun file privato nella media library o in directory pubbliche.

Le entità riunione includono gli argomenti nello snapshot JSON, le mappe includono feature/segnali con ID stabili. Relazioni validate dal dominio sul server; documenti multi-area tramite array di ID senza duplicare il file. Transazioni e vincolo di versione proteggono aggiornamenti concorrenti. I form inviano `expected_version` e `request_id`; mismatch produce HTTP 409 e revisione corrente, senza sovrascrittura. Timestamp del database UTC, visualizzazione Europe/Rome; date di calendario ISO senza conversione di fuso. Migrazione ripetibile, disinstallazione e aggiornamento conservano dati.

## Autorizzazioni

Auth WordPress e nonce REST per browser. L'assegnazione al cantiere è l'autorizzazione applicativa; il ruolo WordPress da solo non concede accesso. Amministratore WordPress configura cantieri, utenti nominativi, imprese e Membership. Referente opera nei cantieri assegnati; lettore consulta ed esporta; impresa scrive propri sinottici/osservazioni e relativi file. Piani confermati di altre imprese consultabili soltanto con condivisione abilitata. Note e foto di altre imprese restano escluse. Controlli ripetuti lato server per ID, revisione, relazioni, export e allegati. Le copie nei backup contengono dati riservati e richiedono custodia adeguata.

## REST

Namespace `hse/v1`. GET paginati (`page`, `per_page`, massimo 500), POST create, PATCH con versione. Risposta `{data: ...}` oppure WP_Error con codice HTTP. Percorsi: sites, areas, companies, memberships, assessments, events, plans, calendar, observations, meetings, actions, toolboxes, sessions, checklists, documents, maps, assets, exports, backup, capabilities.

Operazioni: `plans/{id}/confirm`, `events/{id}/formalize`, `meetings/prepare`, `meetings/{id}/refresh`, `meetings/{id}/finalize`, `toolboxes/prepare`, `toolboxes/{id}/sessions`, `maps/import`, `{risorsa}/{id}/revisions`. DELETE soft soltanto per bozze consentite: stato Discarded, nessuna cancellazione di revisioni. Allegati GET autenticati come base64 JSON, mai URL permanenti pubblici. Questo facilita portabilità ma richiede memoria proporzionale al file; limite 15 MB/file.

## Confini di stato

Una bozza o un download non pubblica sinottici. Il calendario utilizza l'ultima revisione confermata per impresa/settimana, conservandola anche durante una successiva bozza. Totali per attività distinti dalle persone uniche dichiarate; discrepanze richiedono motivazione. Compresenza significa stessa area/giorno e imprese diverse, non sovrapposizione temporale accertata.

Finalizzare una riunione congela fonti e crea/aggiorna azioni collegate nella stessa transazione; non invia email e non firma. Toolbox preparato e incontri svolti sono record distinti. Nessun bonus automatico da generazione/download. Nessun effetto sul Risk Index da sopralluoghi, calendario o mappa.

## Importazioni e dipendenze

KML/KMZ: nessuna estrazione di file su percorsi del documento; limiti 15 MB compressi/KML, 50 MB decompressi, 200 file, rapporto 200:1, 10.000 feature. Traversal, tipi non ammessi, XML attivo/entità e coordinate errate rifiutati. NetworkLink e overlay non collaudati segnalati e ignorati. Proiezione locale north-up su sfondo neutro, nessuna ricostruzione satellitare. Categorie confermate dall'utente; pittogrammi personalizzati senza conformità normativa attribuita.

OCR/PDF locale browser: worker, WASM e italiano inclusi; niente chiamate OCR esterne. Testo PDF con coordinate native, OCR per scansioni; rotazione, ritaglio, rettifica prospettica a quattro vertici. Colonne mappate esplicitamente, valori originali e riquadri mantenuti. Il parser raggruppa per righe spaziali o bande definite dalla griglia/utente; supporta celle multilinea, riestrazione con correzioni conservate e revisione Fonte/Dati. Layout complessi richiedono mapping manuale; accuratezza sul campione reale non certificata. Limiti 5 pagine/20 megapixel, timeout 120 secondi per OCR, annullamento disponibile.

Licenze/versioni: `package-lock.json` e `hse-risk-platform/THIRD_PARTY_LICENSES.txt`. Override image-size 2.0.3 e uuid 11.1.1 correggono advisory transitivi; audit production eseguito senza vulnerabilità segnalate nella verifica del 19 ottobre 2026.

## Motore 2.0.0 verificato

`includes/risk.php` e `risk-catalog.json`: porting delle funzioni pure del documento fornito; nessuna dipendenza Python sul sito. Contratto completo, coefficienti e provenienza in [MODEL_2_0_0.md](MODEL_2_0_0.md). Calcolo e scenario temporanei, salvataggio esplicito idempotente, hash degli input/politica, risultati ricalcolati dal server, storico e confronti autorizzati. Le bozze non cancellano revisioni Saved. Nessun evento da calendario, sopralluogo o download è conteggiato implicitamente.

Gli export persistono snapshot e SHA-256 dei dati di origine; il digest non è una firma del file binario generato nel browser. Il widget Elementor opzionale richiama lo stesso shortcode e archivio. Nessuna migrazione di dati reali; schema invariato e aggiornamento additivo. I vecchi draft mantengono i valori; soltanto cataloghi riconosciuti possono essere calcolati.
