# Gate prima del rilascio

Questa è una checklist di verifiche ancora da eseguire, non un esito positivo.

- [x] Sorgente 2.0.0 ricevuto; porting PHP verificato contro Python su 357 casi e 2.142 scenari, REST e browser. Vedere MODEL_2_0_0.md.
- [ ] Collaudare importazioni su 20 sinottici rappresentativi con trascrizione manuale e metriche per campo/riga/giorno. Verificare celle unite, righe multilinea, 8 date reali, scansioni multipagina e foto inclinate.
- [ ] Completare i controlli manuali WCAG A/AA: lettore di schermo, focus su tutti i percorsi/errori, tastiera, contrasto di tutti gli stati, zoom 200%, orientamento e tastiera a schermo. Axe non certifica conformità.
- [ ] Prove su iOS/Safari e Android/Chrome reali; almeno cinque utilizzatori, attività richieste entro 60 secondi, errori registrati.
- [ ] Aprire e rivedere tutti i template finali in Word/Excel/PowerPoint e lettore PDF; verificare leggibilità di tabelle lunghe, appendici, KPI, accessibilità dei file e corrispondenza PPTX/PDF.
- [ ] Con Elementor effettivamente installato, inserire shortcode, verificare stessa UI/dati e permanenza delle funzioni dopo disattivazione.
- [ ] Su AlterVista: confermare plugin personalizzati, versioni PHP/WordPress, InnoDB, mysqli/ZIP/XML/fileinfo/mbstring (GD facoltativa per il plugin), HTTPS, memoria, upload/post_max_size, max_execution_time e storage database per foto riservate.
- [ ] Su hosting: verificare esclusioni cache anche con REST in query string, mancata indicizzazione, cookie autenticati, file negati da account senza assegnazione, upload interrotti e retry.
- [ ] Backup completo e ripristino su una nuova installazione staging; conservazione dati/revisioni dopo aggiornamento/disinstallazione.
- [ ] Revisione dei modelli toolbox/checklist da parte dell'HSE; nessuna qualificazione normativa dei simboli personalizzati.
- [ ] Approvazione separata del rilascio; nessuna migrazione o pubblicazione in produzione è autorizzata da questa preparazione.

## Gate hosting per la 0.2.1

- [x] PHP 8.0.30 effettivo: parsing, API, calcolo, REST, foto, OCR/export e installazione WordPress locale.
- [x] Installer WordPress accetta la 0.2.1; attivazione e quattro tabelle InnoDB con prefisso non standard; dati conservati alla riattivazione.
- [ ] Sul piano AlterVista effettivo: WordPress ≥6.6, estensioni mysqli/mbstring/fileinfo/SimpleXML/ZIP, permessi CREATE/ALTER e InnoDB.
- [ ] PHP memory_limit 256 MB, upload 32 MB/post 48 MB o caricamento via gestore file/FTP, spazio DB e max_allowed_packet adeguati ai file grandi.
- [ ] HTTPS, cache privata/REST esclusa, worker/WASM/font locali e limiti di esecuzione sul piano reale.

La verifica di PHP 8.0.30 non certifica automaticamente tali impostazioni del piano AlterVista.

- [ ] Su René/AlterVista verificare il template **HSE Platform · applicazione a pagina intera**, login, risorse, layout, cache e rollback in staging; nessuna impostazione di produzione è stata cambiata dal redesign.
