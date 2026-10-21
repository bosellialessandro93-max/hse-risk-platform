"""Explicit manual submission; no access to application records or attachments."""
import streamlit as st
from streamlit_app.gemini import TASKS, AssistanceUnavailable, assist, settings


def render():
    st.title('Assistenza AI')
    st.caption('Google Gemini · supporto alla revisione umana. Le risposte non modificano dati, formule o risultati salvati.')
    try:
        secrets = st.secrets.to_dict()
    except FileNotFoundError:
        secrets = {}
    config = settings(secrets)
    if not config['enabled']:
        st.info('Gemini è disattivato. L’amministratore può configurarlo nei Secrets Streamlit; nessun dato viene trasmesso.')
        return
    st.warning('Invia solo il testo necessario, privo di credenziali e dati personali. Il testo sarà trasmesso a Google dopo il tuo comando.')
    classifications = {'Dati pubblici': 'public', 'Dati sintetici di collaudo': 'synthetic'}
    if config['confidential_authorized']:
        classifications['Dati riservati (trattamento autorizzato)'] = 'confidential'
    else:
        st.info('Dati aziendali riservati: invio disabilitato finché autorizzazioni e condizioni di trattamento non sono verificate.')
    with st.form('gemini_manual', clear_on_submit=False):
        task = st.selectbox('Attività assistita', list(TASKS), key='hse_ai_task')
        classification = st.selectbox('Classificazione del testo', list(classifications), key='hse_ai_classification')
        text = st.text_area('Testo da analizzare', max_chars=20000, height=240,
                            key='hse_ai_text',
                            help='Incolla un estratto da rivedere. Nessun documento o record viene caricato automaticamente.')
        consent = st.checkbox('Confermo la classificazione e autorizzo questo invio a Google Gemini.', key='hse_ai_consent')
        submitted = st.form_submit_button('Invia il testo a Gemini', type='primary')
    if submitted:
        try:
            with st.spinner('Analisi del testo selezionato…'):
                answer = assist(secrets, task=task, text=text,
                                classification=classifications[classification], consent=consent)
            st.subheader('Suggerimento da verificare')
            # Plain text: model output cannot introduce links, HTML, or remote images.
            st.text(answer)
        except AssistanceUnavailable as exc:
            st.error(str(exc))
