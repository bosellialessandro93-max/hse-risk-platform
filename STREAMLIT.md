# HSE Risk Platform — Streamlit

Repository `bosellialessandro93-max/hse-risk-platform`, branch `streamlit-port`, avvio **`app.py`** nella radice. Base: `redesign-ux-0.3.0`, commit `967ea32`. La versione WordPress, i suoi ZIP, formule, cataloghi, API e schema restano invariati.

## Architettura e funzionalità

Streamlit ospita autenticazione, account e sessioni. Un componente locale riusa l’interfaccia JavaScript completa, incluse dashboard Wind/Solar/BESS, wizard, profili per cantiere, NC/ispezioni/detection, calcoli temporanei e salvataggi espliciti, scenari, storico/confronti, sinottici, calendario, sopralluoghi/foto/annotazioni, riunioni, azioni, toolbox/incontri, documenti, checklist, KML/KMZ e backup/ripristino. PDF, DOCX, XLSX, PPTX, JSON, ICS e tavole PNG/PDF sono generati nel browser con le librerie già incluse. OCR italiano e PDF.js usano worker/WASM locali, senza API esterne. Contesto del cantiere conservato nel parametro `hse_site` dell’URL.

Non è un’app solo Python: **PHP CLI è necessario**. Streamlit invoca i moduli HSE PHP già verificati attraverso un adattatore limitato alle funzioni di persistenza/identità usate dal dominio. Non carica WordPress, non richiede il sito AlterVista, non espone un endpoint PHP o una seconda porta, e non avvia HSE-Advisor. Il componente invia richieste tramite il protocollo Streamlit; l’identità è sempre ricavata dalla sessione server, mai dai dati del browser. `streamlit_app/runtime` contiene l’adattatore; `hse-risk-platform/includes` contiene i moduli originali, letti senza modificarli.

## Deploy Streamlit Community Cloud

1. Da Community Cloud scegliere **Create app → GitHub**. Repository `bosellialessandro93-max/hse-risk-platform`, branch **`streamlit-port`**, main file **`app.py`**. In Advanced settings scegliere **Python 3.12**.
2. Scegliere **Neon/PostgreSQL 14+** (istruzioni sotto) oppure un **database dedicato esterno MySQL 8 / MariaDB 10.6+**, InnoDB, raggiungibile dal servizio Cloud. Le istruzioni MySQL nei punti 2–3 restano valide per quel backend. Non usare il database produttivo WordPress. Occorrono transazioni, lock di riga e `GET_LOCK`; assegnare all’utente applicativo SELECT/INSERT/UPDATE/DELETE/CREATE/ALTER/INDEX sul solo database dedicato. Il database deve esistere già; l’app crea le proprie tabelle con prefisso `st_`.
3. In **App → Settings → Secrets**, copiare il modello [.streamlit/secrets.toml.example](.streamlit/secrets.toml.example) e sostituire tutti i placeholder. Impostare `database.host`, `port`, `name`, `user`, `password`, `prefix`, `tls = true`; se il provider usa una CA privata, aggiungere il PEM in `ca_certificate`. Entrambi i client MySQL verificano il certificato. `tls = false` è stato usato esclusivamente nella rete Docker privata di collaudo.
4. Selezionare l’autenticazione come descritto sotto e salvare i Secrets. `requirements.txt` installa Streamlit/PyMySQL/psycopg; **`packages.txt` installa PHP CLI, mysqli, pgsql, mbstring, XML/SimpleXML e ZIP**. PHP minimo 8.0.30. Gli asset sono già compilati e versionati: non occorre eseguire Node/npm, installare WordPress o usare un servizio HTTP aggiuntivo.
5. Avviare l’app. Con un account amministrativo creare cantieri, aree e imprese, quindi gli account e le assegnazioni. Verificare health, login, calcolo/salvataggio e download prima di usare dati reali. Il deploy sul proprio account Cloud e l’installazione APT in quell’ambiente non sono stati eseguiti durante questo collaudo.

Mantenere invariati database, prefisso e Secrets tra riavvii/redeploy. Dimensionare quota DB, connessioni e, su MySQL, `max_allowed_packet` (almeno 32 MB, consigliati 64 MB per allegati/backup). Limite per allegato 15 MB; massimo richiesta 64 MB. Tutti i record, le revisioni, le richieste idempotenti, gli account e i binari sono nel database esterno. L’app **non crea SQLite o archivi JSON locali di ripiego**. Il filesystem temporaneo è usato soltanto per elaborare upload/KMZ/CA e i file vengono rimossi; gli asset statici sono nel repository. Predisporre backup e retention sul servizio database: i backup logici della UI mantengono il perimetro originale e non sostituiscono il backup completo di account, assegnazioni e revisioni.

## Neon: configurazione pronta per Streamlit

Neon usa PostgreSQL ed è ora supportato accanto a MySQL. Non occorrono WordPress o un database MySQL aggiuntivo. **Non modificare le credenziali o il database dell’altro tool.** Nello stesso progetto Neon creare un database separato, per esempio `hse_streamlit`, dalla pagina **Branches → branch scelto → Databases → New database** (la posizione può variare con la console). Scegliere un ruolo proprietario di quel database; non sono necessari privilegi di superuser. L’app deve poter creare tabelle, indici e sequenze e leggere/scrivere le proprie tabelle. Non crea o elimina altri database o dati dell’altro tool.

1. In Neon cliccare **Connect**, scegliere il branch, **Database: hse_streamlit**, e il ruolo. Sono supportati endpoint diretti e **Connection pooling**. Copiare **Connection string**, solo il testo che comincia con `postgresql://`, senza il comando `psql` né virgolette esterne. Conservare `sslmode=require` e, se presente, `channel_binding=require`.
2. In **Streamlit → App settings → Secrets**, eliminare l’esempio/MySQL precedente e incollare il contenuto di [.streamlit/secrets.neon.toml.example](.streamlit/secrets.neon.toml.example). Sostituire `database.url` con la stringa appena copiata e `bootstrap_password` con una password casuale di almeno 12 caratteri. Non condividere questi valori in chat, log o repository.
3. Salvare; attendere l’aggiornamento delle dipendenze dal branch `streamlit-port`, eventualmente usare **Reboot app**. Repository, branch, `app.py` e Python 3.12 non cambiano. Al primo accesso usare `administrator` e la password scelta. Le tabelle `st_users`, `st_options`, `st_login_limits`, `st_hse_records`, `st_hse_revisions`, `st_hse_requests`, `st_hse_assets` vengono create automaticamente nel database selezionato.

In alternativa al nuovo database si può usare un database PostgreSQL già esistente **con un prefisso esclusivo**, per esempio `prefix = "hse_streamlit_"`, verificando che non sia già usato. Il prefisso non è un confine di autorizzazione: database/ruolo dedicati garantiscono una separazione più forte. Non cambiare URL/database/prefisso dopo aver inserito dati, altrimenti si seleziona un archivio diverso. Non viene effettuata alcuna migrazione automatica da MySQL o WordPress. I binari/foto sono `bytea` nel database esterno: concorrono alla quota Neon. Monitorare spazio, connessioni, backup e limiti del piano corrente del provider; nessun ripiego su disco effimero.

La connessione è cifrata. È supportato anche `sslmode=verify-full`, con le CA di sistema; `sslmode=disable` è riservato ai test locali. Le transazioni, gli advisory lock transazionali e gli UPSERT mantengono il comportamento di revisioni, idempotenza, bootstrap amministratore e blocco tentativi anche con un pooler in modalità transaction. I moduli originali del Risk Index e WordPress non vengono modificati. Non servono `search_path`, lock di sessione o un server PHP pubblico.

Il collaudo PostgreSQL è documentato in [docs/STREAMLIT_POSTGRES_QA.json](docs/STREAMLIT_POSTGRES_QA.json). Usa database/credenziali sintetici locali: non prova l’accesso al progetto Neon dell’utente né il deploy sul suo account Community Cloud.

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

### QA PostgreSQL

Con PHP CLI e le estensioni di `packages.txt`, dipendenze Python già installate e un **database PostgreSQL dedicato esclusivamente al collaudo**:

```sh
# Impostare HSE_TEST_DATABASE_URL fuori da file versionati, con la URL del database QA.
python tools/test-streamlit-postgres.py
# Per il browser, lasciare aperto il server QA:
HSE_QA_DIR=.local/streamlit-postgres-qa python tools/run-streamlit-local.py
HSE_QA_DIR=.local/streamlit-postgres-qa node tests/streamlit/browser.mjs
```

Il runner genera un prefisso isolato e credenziali amministrative casuali, conservate solo nella directory ignorata `.local/streamlit-postgres-qa`. Non stampa la URL/password. Per un browser in un percorso diverso: `HSE_CHROMIUM_PATH=/percorso/chromium`. I dati sintetici restano nel solo database di collaudo per le verifiche browser. La suite comprende gli stessi 39 flussi backend, 357 modelli/2.142 scenari, autenticazione/sessioni e controlli PostgreSQL di concorrenza, rollback e binari; non è un test del provider OIDC o della console Neon.
