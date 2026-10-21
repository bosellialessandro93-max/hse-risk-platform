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

### Collegamento tramite Neon CLI (`neon.ts`)

Il progetto dedicato indicato dall’utente è `wild-cherry-76203069`, organizzazione `org-crimson-rice-09249677`, branch Neon `production` (distinto dal branch GitHub `streamlit-port`). `neon.ts` conserva il solo servizio PostgreSQL e l’autenticazione nativa HSE; gli SDK Node `@neon/config`/`@neon/env` sono dipendenze di **sviluppo/provisioning**, non del runtime Streamlit. Psycopg e PHP pgsql restano i driver applicativi.

Su una macchina che può raggiungere Neon:

```sh
npx neon@latest login
npx neon@latest init -y --org-id org-crimson-rice-09249677 --project-id wild-cherry-76203069 --branch production --services postgres --no-agent-setup
npx neon@latest deploy
# Se necessario, aggiornare soltanto le variabili:
npx neon@latest env pull
npm run build
streamlit run app.py
```

`init --no-agent-setup` configura il progetto senza modificare la configurazione personale dell’AI client. La CLI può scrivere `.neon` anche **offline**: ciò non dimostra autenticazione, provisioning o accesso al database. `deploy` deve riuscire prima di considerare il servizio verificato. Le istruzioni operative dei Neon agent skills sono state consultate; nessuna funzione/auth/storage aggiuntivi sono necessari a questa app.

L’app legge `DATABASE_URL` per le operazioni normali e, se fornita insieme, `DATABASE_URL_UNPOOLED` per la creazione/aggiornamento delle tabelle (Python e PHP). Le variabili di processo prevalgono sui file; in locale `.env.local` prevale su `.env`, senza cercare file in altri repository. Sono mantenuti `[database]` dei Secrets e `HSE_DATABASE` per configurazioni esplicite/QA. `[database]` esplicito prevale sulle URL d’ambiente. Il prefisso opzionale è `HSE_DATABASE_PREFIX`, predefinito `st_`. Un esempio privo di credenziali è in [.env.example](.env.example). Non caricare `.env`, `.env.local` o `.neon` su GitHub.

Su **Community Cloud** la CLI eseguita sul proprio PC non aggiorna automaticamente i Secrets: copiare lì i valori reali ottenuti da Neon. Si può continuare con il precedente `[database] url`, oppure usare questo formato (chiavi URL **prima** delle sezioni TOML):

```toml
DATABASE_URL = "INCOLLARE_URL_POOLER_DA_NEON"
DATABASE_URL_UNPOOLED = "INCOLLARE_URL_DIRETTA_DA_NEON"

[hse_auth]
mode = "password"
bootstrap_username = "administrator"
bootstrap_password = "REPLACE_WITH_RANDOM_PASSWORD_AT_LEAST_12_CHARACTERS"
```

Le due URL devono appartenere allo **stesso database**, branch e ruolo. Non combinare una URL applicativa con un archivio diverso per lo schema. Se si usa solo `[database] url`, il bootstrap resta transazionale e funziona anche con il pooler già collaudato. La password bootstrap deve essere sostituita. La CLI Neon non pubblica il frontend Streamlit.

**Esito di questa configurazione:** CLI `8.10.1` installata; `init` completato con collegamento scritto offline. `login`, `deploy` ed `env pull` bloccati dall’accesso alle API (`CONNECT tunnel failed, response 403` dal proxy dell’ambiente). Nessuna credenziale Neon recuperata e nessuna modifica remota confermata. Build e verifiche PostgreSQL locali sono distinti da una verifica end-to-end sul progetto Neon reale. Dettagli in [docs/NEON_SETUP_STATUS.json](docs/NEON_SETUP_STATUS.json).

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

## Ottimizzazioni e design Streamlit (ottobre 2026)

Il componente carica export Office/PDF, PDF.js e Tesseract solo quando necessari. `npm run build` produce ora moduli ES e chunk locali versionati: distribuire l'intera cartella `streamlit_app/frontend`, non il solo `app.bundle.js`. Il builder mantiene invariati gli asset e i moduli WordPress; interrompe la build se cambiano i confini principali dell'adattamento.

Il bridge raggruppa fino a 16 letture adiacenti nello stesso passaggio Streamlit e nello stesso processo PHP/connessione DB. Ogni sottorichiesta passa ancora dalle autorizzazioni originali. Le scritture restano singole e mantengono ordine, idempotenza e controllo delle revisioni. La condivisione di GET identiche vale solo mentre sono in corso: nessuna nuova cache persistente di dati o permessi. I contatori dashboard richiedono il totale e un solo record, evitando di trasportare al browser l'intero archivio. L'account viene ricontrollato a ogni esecuzione Streamlit; è stata rimossa soltanto la seconda interrogazione identica nello stesso run.

Il tema industriale è circoscritto al componente Streamlit: navy, blu tecnico, teal, verde sicurezza, arancione visibilità e grigi chiari. Si applica a dashboard, moduli, calendario, documenti, mappe, storico ed export. La navigazione tiene conto della larghezza dell'iframe. I ruoli esistenti determinano i moduli accessibili. Nessun dato o comando dimostrativo viene introdotto nel prodotto. Gli slot per logo e riferimenti futuri sono descritti in `streamlit_app/ui/README.md`; il manifest vuoto mantiene le illustrazioni già esistenti.

Misure ripetibili e limiti: [docs/STREAMLIT_IMPROVEMENTS_QA.json](docs/STREAMLIT_IMPROVEMENTS_QA.json). Su cinque sessioni Chromium nuove in locale, mediana login→dashboard completa **2.691 → 1.249 ms**, passaggi bridge **8 → 4**, JavaScript iniziale **3.571.820 → 88.051 byte**. Ritorno alla panoramica **754 → 201 ms**; le altre navigazioni rimangono circa 187–205 ms, con variazioni in entrambe le direzioni. Sono misure su dati sintetici e PostgreSQL locale: non rappresentano latenza, cold start o carico del Neon/Streamlit Cloud aziendale. Nessuna connessione o scrittura sul database reale è stata effettuata.

Con un database QA dedicato e il runtime documentato:

```sh
HSE_QA_DIR=.local/streamlit-postgres-qa python tests/streamlit/batch.py
python tests/streamlit/gemini.py
node tests/streamlit/bridge.mjs
HSE_QA_DIR=.local/streamlit-postgres-qa node tests/streamlit/performance.mjs
HSE_QA_DIR=.local/streamlit-postgres-qa node tests/streamlit/design-qa.mjs
HSE_QA_DIR=.local/streamlit-postgres-qa node tests/streamlit/roles.mjs
HSE_QA_DIR=.local/streamlit-postgres-qa HSE_QA_PYTHON=python node tests/streamlit/accounts-ui.mjs
```

Il benchmark usa cinque contesti browser nuovi; `HSE_PERF_OUTPUT` seleziona il file di risultato. Eseguire prima la suite PostgreSQL e avviare il server QA come sopra. Le credenziali sintetiche restano nei file ignorati. I controlli axe automatici non costituiscono certificazione WCAG; i riferimenti grafici approvati, il test con screen reader e le misure sulla produzione restano separati.

## Assistenza opzionale Google Gemini

La voce **Assistenza AI** non legge automaticamente record, documenti o dati Neon. Supporta analisi NC, lettura di estratti documentali, spiegazione dei risultati forniti e raccomandazioni da verificare. L'utente incolla il testo, dichiara la classificazione e conferma esplicitamente ogni invio. Le risposte sono testo da rivedere: non cambiano dati, permessi o Risk Index e non vengono registrate automaticamente.

Aggiungere esclusivamente nei **Secrets Streamlit** la sezione del modello `.streamlit/secrets.gemini.toml.example`, inserendo lì la chiave reale. Nessuna lettura di `GEMINI_API_KEY` dall'ambiente o dal browser. La chiave viene inviata lato server nell'header HTTPS verso `generativelanguage.googleapis.com`; non compare in URL, log, frontend o messaggi d'errore. Per attivare sui soli dati pubblici/sintetici impostare `enabled = true` e scegliere un modello disponibile nel proprio account. Il provider richiede rete, chiave e quota valide; il collaudo di questo intervento usa risposte simulate, non una chiamata reale.

Lasciare `processing_authorized` e `allow_confidential_data` a `false`: i dati riservati restano bloccati anche se Gemini è attivato. Le due impostazioni possono essere abilitate soltanto dopo verifica delle autorizzazioni e delle condizioni di trattamento, fuori da questo intervento. Nessuna verifica legale o autorizzazione viene dedotta dall'esistenza di una chiave. Non inserire segreti nella chat o nei file versionati.

### Interfaccia corporate dal riferimento grafico

L'aggiornamento successivo sostituisce l'header, la navigazione e la homepage del componente con una composizione derivata dall'immagine fornita: hero fotografica, marchio, quattro passaggi operativi, font e icone locali. Le assegnazioni reali determinano dashboard e comandi. I 17 moduli restano accessibili dal pulsante Moduli. La barra standard Streamlit viene nascosta; gestione account, profilo personale, cambio password e logout restano raggiungibili dai comandi effettivi dell'interfaccia. CSS, bridge e bundle hanno URL versionati per aggiornare gli asset dopo il deploy.

Assistenza AI è disponibile anche nel componente, con stato dei Secrets e guida amministrativa. Sono riconosciute le voci radice `Gemini API Key`, `GEMINI_API_KEY`, `GOOGLE_API_KEY` o `[gemini].api_key`; rimane necessaria l'abilitazione esplicita `[gemini] enabled = true`. La chiave non viene restituita al browser. Non sostituire i Secrets Neon: aggiornare la sezione Gemini esistente, senza duplicarla. Dettagli, licenze e collaudo con provider simulato in [streamlit_app/ui/README.md](streamlit_app/ui/README.md); risultati e limiti in [docs/STREAMLIT_CORPORATE_QA.json](docs/STREAMLIT_CORPORATE_QA.json).
