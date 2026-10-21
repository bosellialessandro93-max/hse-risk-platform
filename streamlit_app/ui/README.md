# Riferimenti grafici approvati

Nessuna immagine definitiva viene generata durante questo intervento. Le illustrazioni già presenti nel progetto restano il fallback Wind/Solar/BESS.

Quando saranno disponibili i riferimenti, collocare i file approvati in `streamlit_app/ui/references/` e registrarli in `brand.json`, poi eseguire `npm run build`. Non inserire immagini o URL riservati, credenziali o riferimenti remoti. I nomi devono essere semplici nomi di file PNG, JPEG, WebP o SVG, senza percorsi. Ogni immagine richiede un testo alternativo pertinente.

Slot disponibili: `logo`, `home`, `dashboard_hse`, `dashboard_company`, `assessment`, `output`, `profiles`, `wind`, `solar`, `bess`.

Esempio di struttura, da compilare soltanto con un riferimento approvato:

```json
{
  "logo": {"file": "logo-approvato.svg", "alt": "HSE Risk Platform"}
}
```

`profiles` viene mostrato nella schermata di accesso Streamlit. Gli altri slot appartengono al componente. Dashboard HSE/Impresa derivano dai permessi reali, non introducono nuovi ruoli. La configurazione vuota non aggiunge immagini o segnaposto.
