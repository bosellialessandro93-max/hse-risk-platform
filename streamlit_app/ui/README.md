# Interfaccia corporate HSE Risk Index

`workspace.js` definisce header, navigazione, homepage e pannello Gemini del solo componente Streamlit. Il builder riusa moduli, form e trasporto autorizzato esistenti e non modifica WordPress o il Risk Index. `design.css` applica il sistema visivo anche agli elenchi, ai moduli, al calendario e ai risultati.

Il riferimento è il mockup corporate allegato dall'utente: header bianco, hero fotografica Wind/Solar/BESS, quattro passaggi, schede chiare e palette navy/blu/teal/arancio. Hero e marchio sono asset generati sulla base di quel riferimento, non fotografie di cantieri dell'utente o il file originale di un marchio ufficiale. Le etichette e i comandi restano legati alle funzionalità reali; non sono stati aggiunti notifiche, persone, KPI o ruoli fittizi.

Inter e le icone Phosphor vengono inclusi localmente nella build, con le rispettive licenze. Nessun CDN necessario. `index.html` è il template; `npm run build` produce l'HTML e i riferimenti con un identificativo di versione per CSS, bridge e bundle.

## Immagini

File in `references/`, registrati in `brand.json`. Slot: `logo`, `home`, `dashboard_hse`, `dashboard_company`, `assessment`, `output`, `profiles`, `wind`, `solar`, `bess`. Dashboard HSE/Impresa derivano dai permessi effettivi. File consentiti: PNG, JPEG, WebP, SVG con semplice nome senza percorsi; ogni voce richiede un testo alternativo. Non usare URL remoti o immagini riservate. Se verrà fornito un logo originale, sostituire il marchio ricostruito nel manifest e ricompilare.

## Gemini e Secrets

Il pannello Assistenza AI è integrato nell'interfaccia. Il server restituisce solo metadati di configurazione: chiave presente, abilitazione, disponibilità e blocco dei dati riservati. La chiave rimane nei Secrets Streamlit; sono accettati `[gemini].api_key` e le voci radice `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `Gemini API Key`. Nessuna lettura della chiave dall'ambiente del processo o dal browser.

Per attivare una chiave già riconosciuta, aggiornare la sezione esistente oppure aggiungerla se manca, senza duplicarla:

```toml
[gemini]
enabled = true
processing_authorized = false
allow_confidential_data = false
```

Se la chiave manca, inserirla come `api_key` nella stessa sezione, esclusivamente nell'editor **Manage app → Settings → Secrets**, mantenendo invariati Neon, database, prefisso e autenticazione. Il modello è configurabile con `model`; il predefinito è `gemini-2.5-flash`. Disponibilità e quota devono essere verificate nell'account Google utilizzato.

Nessun invio automatico, nessuna lettura automatica di record o allegati. Il consenso è richiesto a ogni invio e viene azzerato dopo la risposta. Gli output sono testo, non HTML eseguibile, e non vengono salvati nei record. I dati riservati restano bloccati finché entrambe le impostazioni di trattamento non sono state autorizzate esternamente. L'app non può modificare autonomamente i Secrets dell'account Streamlit.

## Collaudo Gemini senza provider reale

Con il database QA locale già preparato:

```sh
python tools/run-gemini-ui-qa.py
# In un altro terminale:
HSE_GEMINI_QA=1 node tests/streamlit/gemini-ui.mjs
```

Il launcher usa una chiave sintetica nella voce `Gemini API Key`, un provider simulato e la porta 8506. Non usa credenziali reali e non invia richieste a Google. Il collaudo percorre login nativo, bridge, riconoscimento del Secret, consenso, risposta e blocco dei riservati.
