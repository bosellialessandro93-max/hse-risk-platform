# HSE Risk Platform — Streamlit

Repository `bosellialessandro93-max/hse-risk-platform`, branch `streamlit-port`, avvio **`app.py`** nella radice. Base: `redesign-ux-0.3.0`, commit `967ea32`. La versione WordPress, i suoi ZIP, formule, cataloghi, API e schema restano invariati.

## Architettura e funzionalità

Streamlit ospita autenticazione, account e sessioni. Un componente locale riusa l’interfaccia JavaScript completa, incluse dashboard Wind/Solar/BESS, wizard, profili per cantiere, NC/ispezioni/detection, calcoli temporanei e salvataggi espliciti, scenari, storico/confronti, sinottici, calendario, sopralluoghi/foto/annotazioni, riunioni, azioni, toolbox/incontri, documenti, checklist, KML/KMZ e backup/ripristino. PDF, DOCX, XLSX, PPTX, JSON, ICS e tavole PNG/PDF sono generati nel browser con le librerie già incluse. OCR italiano e PDF.js usano worker/WASM locali, senza API esterne. Contesto del cantiere conservato nel parametro `hse_site` dell’URL.

Non è un’app solo Python: **PHP CLI è necessario**. Streamlit invoca i moduli HSE PHP già verificati attraverso un adattatore limitato alle funzioni di persistenza/identità usate dal dominio. Non carica WordPress, non richiede il sito AlterVista, non espone un endpoint PHP o una seconda porta, e non avvia HSE-Advisor. Il componente invia richieste tramite il protocollo Streamlit; l’identità è sempre ricavata dalla sessione server, mai dai dati del browser. `streamlit_app/runtime` contiene l’adattatore; `hse-risk-platform/includes` contiene i moduli originali, letti senza modificarli.

## Deploy Streamlit Community Cloud

1. Da Community Cloud scegliere **Create app → GitHub**. Repository `bosellialessandro93-max/hse-risk-platform`, branch **`streamlit-port`**, main file **`app.py`**. In Advanced settings scegliere **Python 3.12**.
2. Provisionare un **database dedicato esterno MySQL 8 / MariaDB 10.6+**, InnoDB, raggiungibile dal servizio Cloud. Non usare il database produttivo WordPress. Occorrono transazioni, lock di riga e `GET_LOCK`; assegnare all’utente applicativo SELECT/INSERT/UPDATE/DELETE/CREATE/ALTER/INDEX sul solo database dedicato. Il database deve esistere già; l’app crea le proprie tabelle con prefisso `st_`.
3. In **App → Settings → Secrets**, copiare il modello [.streamlit/secrets.toml.example](.streamlit/secrets.toml.example) e sostituire tutti i placeholder. Impostare `database.host`, `port`, `name`, `user`, `password`, `prefix`, `tls = true`; se il provider usa una CA privata, aggiungere il PEM in `ca_certificate`. Entrambi i client MySQL verificano il certificato. `tls = false` è stato usato esclusivamente nella rete Docker privata di collaudo.
4. Selezionare l’autenticazione come descritto sotto e salvare i Secrets. `requirements.txt` installa Streamlit/PyMySQL; **`packages.txt` installa PHP CLI, mysqli, mbstring, XML/SimpleXML e ZIP**. PHP minimo 8.0.30. Gli asset sono già compilati e versionati: non occorre eseguire Node/npm, installare WordPress o usare un servizio HTTP aggiuntivo.
5. Avviare l’app. Con un account amministrativo creare cantieri, aree e imprese, quindi gli account e le assegnazioni. Verificare health, login, calcolo/salvataggio e download prima di usare dati reali. Il deploy sul proprio account Cloud e l’installazione APT in quell’ambiente non sono stati eseguiti durante questo collaudo.

Mantenere invariati database, prefisso e Secrets tra riavvii/redeploy. Dimensionare quota DB, connessioni e `max_allowed_packet` (almeno 32 MB, consigliati 64 MB per allegati/backup). Limite per allegato 15 MB; massimo richiesta 64 MB. Tutti i record, le revisioni, le richieste idempotenti, gli account e i binari sono nel database esterno. L’app **non crea SQLite o archivi JSON locali di ripiego**. Il filesystem temporaneo è usato soltanto per elaborare upload/KMZ/CA e i file vengono rimossi; gli asset statici sono nel repository. Predisporre backup e retention sul servizio database: i backup logici della UI mantengono il perimetro originale e non sostituiscono il backup completo di account, assegnazioni e revisioni.

## Autenticazione e profili

**Password:** `[hse_auth] mode = "password"`, `bootstrap_username`, `bootstrap_password` casuale di almeno 12 caratteri. Il bootstrap crea il primo amministratore solo se la tabella account è vuota; non sovrascrive account esistenti. Dopo il primo accesso si può rimuovere la password bootstrap dai Secrets. Non sostituisce una procedura di recupero: mantenere almeno due amministratori se serve un reset da interfaccia. Nessuna password predefinita è incorporata. Hash PBKDF2-SHA256 con salt casuale e 600.000 iterazioni; cinque tentativi falliti bloccano l’account per 15 minuti. La sidebar consente il cambio della propria password; gli amministratori creano/disabilitano account e reimpostano password. Reset e disabilitazione revocano le altre sessioni alla successiva richiesta. Il login password dura nella sessione Streamlit: dopo refresh/restart occorre accedere nuovamente; i dati restano nel DB.

**SSO OIDC:** `[hse_auth] mode = "oidc"`, `admin_emails` e facoltativamente `allowed_domains`; aggiungere la sezione standard Streamlit `[auth]` con `redirect_uri = "https://NOME-APP.streamlit.app/oauth2callback"`, `cookie_secret` stabile casuale, `client_id`, `client_secret`, `server_metadata_url` e scope `openid email profile`. Registrare la stessa callback nel provider. È richiesto il claim **`email_verified = true`** e un’email: provider che non lo emettono devono essere configurati opportunamente. Il primo login verificato crea l’identità; quelle non amministrative restano senza cantieri finché assegnate. La cookie/sessione OIDC è gestita da Streamlit. Sono stati testati provisioning e rifiuto dei claim non verificati; il flusso presso un provider reale non è stato eseguito perché mancano client/Secrets del provider.

**Ruoli applicativi invariati:** amministratore globale, referente HSE `manager`, lettore `reader`, Impresa `company`. In **Account utenti** vedere gli ID nativi; usarli in **Archivio e impostazioni → Assegnazioni**. L’ID è dell’account Streamlit, non dell’utente WordPress. I profili mantengono i perimetri per cantiere/impresa e i piani condivisi originali. Gli account/password WordPress non vengono importati automaticamente: richiedono un piano esplicito di migrazione identità. Le cache delle risposte vengono eliminate quando cambia o scade l’identità.

## Sviluppo e collaudo

Avvio locale, con Python 3.12, PHP CLI e database esterno già configurati:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
# Impostare .streamlit/secrets.toml usando il modello, escluso da Git.
streamlit run app.py
```

Per ricompilare il solo componente: `npm ci && node tools/build-streamlit.mjs`. Il build legge gli asset originali e sostituisce solo il trasporto API e l’etichetta dell’ID account; non modifica i file WordPress. Licenze incluse nel componente.

QA Linux con i container di test del repository già disponibili (`hse-db`, `hse-wp-php80`), senza caricare WordPress nel runtime standalone:

```sh
pip install -r requirements-dev.txt
npm ci
python tools/prepare-streamlit-qa.py
python tools/run-streamlit-local.py   # altro terminale, porta 8505
python tools/test-streamlit.py
```

Il preparatore crea solo `hse_streamlit_test`/utente SQL dedicato e un file ignorato `.local/streamlit-test-env.json`; non stampa password. I test scrivono solo dati sintetici in quel DB. Per il controllo di riavvio: `python tests/streamlit/persistence.py --before`, interrompere e riavviare soltanto il processo QA sulla porta 8505, poi `python tests/streamlit/persistence.py`. Il test PHP `tests/streamlit/runtime.php` va eseguito nello stesso runtime PHP con il repository disponibile. Le dipendenze di test non sono richieste dall’app pubblicata.

Esiti e limiti verificati sono in [docs/STREAMLIT_QA.json](docs/STREAMLIT_QA.json). Nessun deploy di produzione o modifica ad AlterVista eseguiti. Restano esterni al collaudo il vero deployment Community Cloud, la connessione TLS al provider scelto, il login OIDC reale, dispositivi mobili/screen reader reali e i collaudi su sinottici industriali rappresentativi già indicati nella documentazione del progetto. Le verifiche axe non certificano WCAG.
