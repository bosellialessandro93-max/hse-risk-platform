"""Run: streamlit run app.py. Durable data lives exclusively in external MySQL/PostgreSQL."""
import json
import os
import re
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from streamlit_app import database
from streamlit_app.gateway import invoke

st.set_page_config(page_title='HSE Risk Platform', page_icon='🛡️', layout='wide')
ROOT = Path(__file__).resolve().parent
workspace = components.declare_component('hse_workspace', path=str(ROOT / 'streamlit_app/frontend'))


def configuration():
    try:
        values = st.secrets.to_dict()
    except FileNotFoundError:
        values = {}
    config = json.loads(os.environ['HSE_DATABASE']) if os.environ.get('HSE_DATABASE') else values.get('database', {})
    auth = json.loads(os.environ['HSE_AUTH']) if os.environ.get('HSE_AUTH') else values.get('hse_auth', {})
    if auth.get('mode', 'password') not in ('password', 'oidc'):
        raise ValueError('Modalità di autenticazione non valida.')
    if auth.get('mode') == 'oidc':
        if not auth.get('admin_emails'):
            raise ValueError('Configurare almeno una email amministrativa OIDC.')
        if any(not values.get('auth', {}).get(key) for key in ('redirect_uri', 'cookie_secret', 'client_id', 'client_secret', 'server_metadata_url')):
            raise ValueError('Configurare il provider OIDC nella sezione auth dei Secrets.')
    return database.validated_config(config), auth


@st.cache_resource
def initialize_storage(config, auth):
    return database.initialize(config, auth)


def stop_error(message):
    st.error(message)
    st.stop()


try:
    config, auth = configuration()
    initialize_storage(config, auth)
except Exception:
    st.title('HSE Risk Platform')
    st.error('Configurazione o database esterno non disponibili. Impostare i Secrets indicati in STREAMLIT.md e verificare TLS, credenziali e permessi. Nessun archivio locale sostitutivo viene creato.')
    st.stop()

if auth.get('mode', 'password') == 'oidc':
    if not st.user.is_logged_in:
        st.title('HSE Risk Platform')
        st.write('Accedi con il tuo account aziendale.')
        if st.button('Accedi', type='primary'):
            st.login()
        st.stop()
    try:
        actor = database.oidc_user(config, st.user.to_dict(), auth)
    except ValueError as error:
        stop_error(str(error))
else:
    try:
        actor = database.get_user(config, st.session_state['user_id']) if st.session_state.get('user_id') else None
    except Exception:
        stop_error('Database esterno non raggiungibile. Riprovare senza creare archivi locali.')
    if not actor and st.session_state.get('user_id'):
        st.session_state.clear()
    if actor and st.session_state.get('login_version') != actor['token_version']:
        st.session_state.clear()
        actor = None
    if not actor:
        st.title('HSE Risk Platform')
        with st.form('login', clear_on_submit=True):
            username = st.text_input('Nome utente', max_chars=254)
            password = st.text_input('Password', type='password', max_chars=512)
            submitted = st.form_submit_button('Accedi', type='primary')
        if submitted:
            try:
                user = database.authenticate(config, username, password)
            except Exception:
                stop_error('Servizio account non raggiungibile. Riprovare più tardi.')
            if user:
                st.session_state['user_id'] = user['id']
                st.session_state['login_version'] = user['token_version']
                st.rerun()
            st.error('Accesso non riuscito. Controlla i dati oppure attendi 15 minuti dopo ripetuti tentativi.')
        st.stop()

# Never deliver response caches or component state belonging to a previous identity.
if st.session_state.get('hse_owner') != actor['id']:
    for key in list(st.session_state):
        if key.startswith(('hse_', 'workspace_')):
            del st.session_state[key]
    st.session_state['hse_owner'] = actor['id']

with st.sidebar:
    st.write('**' + actor['display_name'] + '**')
    st.caption(f"ID account: {actor['id']} · {'Amministratore' if actor['is_admin'] else 'Permessi per cantiere'}")
    if st.button('Esci'):
        st.session_state.clear()
        if auth.get('mode') == 'oidc':
            st.logout()
        st.rerun()
    if auth.get('mode', 'password') == 'password':
        with st.expander('Cambia password'):
            with st.form('own_password', clear_on_submit=True):
                previous = st.text_input('Password attuale', type='password', max_chars=512)
                replacement = st.text_input('Nuova password personale', type='password', max_chars=512)
                if st.form_submit_button('Cambia password'):
                    try:
                        st.session_state['login_version'] = database.change_password(config, actor, previous, replacement)
                        st.success('Password aggiornata; le altre sessioni dovranno accedere nuovamente.')
                    except ValueError as error:
                        st.error(str(error))
    page = st.radio('Spazio di lavoro', ['Piattaforma', 'Account utenti'] if actor['is_admin'] else ['Piattaforma'], label_visibility='collapsed')

if page == 'Account utenti':
    st.title('Account utenti')
    st.caption('Usa gli ID qui elencati in Archivio e impostazioni → Assegnazioni. Ruoli e perimetri dei cantieri restano separati dai privilegi amministrativi.')
    try:
        st.dataframe(database.manage_users(config, actor), hide_index=True)
        with st.form('new_user', clear_on_submit=True):
            username = st.text_input('Nome utente nuovo account')
            name = st.text_input('Nome visualizzato')
            password = st.text_input('Password iniziale (almeno 12 caratteri)', type='password')
            admin = st.checkbox('Amministratore della piattaforma')
            if st.form_submit_button('Crea account'):
                database.manage_users(config, actor, create={'username': username, 'display_name': name, 'password': password, 'is_admin': admin})
                st.success('Account creato. Assegna i cantieri nella piattaforma.')
                st.rerun()
        with st.form('edit_user'):
            uid = st.number_input('ID account da aggiornare', min_value=1, step=1)
            active = st.checkbox('Account attivo', value=True)
            admin = st.checkbox('Privilegi amministrativi')
            if st.form_submit_button('Aggiorna account'):
                database.manage_users(config, actor, update={'id': uid, 'active': active, 'is_admin': admin})
                st.rerun()
        with st.form('reset_password', clear_on_submit=True):
            uid = st.number_input('ID account per nuova password', min_value=1, step=1)
            password = st.text_input('Nuova password', type='password')
            if st.form_submit_button('Imposta password'):
                database.manage_users(config, actor, update={'id': uid, 'password': password})
                st.success('Password aggiornata.')
    except (ValueError, PermissionError) as error:
        st.error(str(error))
    except Exception:
        st.error('Operazione account non riuscita; verificare che il nome utente sia univoco.')
    st.stop()

try:
    if not st.session_state.get('hse_bootstrapped'):
        response = invoke(config, actor, action='bootstrap')
        if response.get('error'):
            stop_error(response['error']['message'])
        st.session_state['hse_bootstrapped'] = True
    responses = st.session_state.setdefault('hse_responses', [])
    request = workspace(config={'admin': bool(actor['is_admin']), 'user': actor['id'], 'selected_site': st.query_params.get('hse_site', '')}, responses=responses, key='workspace_' + str(actor['id']), default=None)
    if isinstance(request, dict) and request.get('id') not in st.session_state.get('hse_processed', []):
        try:
            selected = request.get('active_site', '') or ''
            if re.fullmatch(r'[0-9a-fA-F-]{36}', selected) and st.query_params.get('hse_site') != selected:
                st.query_params['hse_site'] = selected
            # Actor always comes from the authenticated server session, never component data.
            actor = database.get_user(config, actor['id'])
            if not actor:
                stop_error('Account non più attivo. Accedi nuovamente.')
            result = invoke(config, actor, request=request)
        except (ValueError, RuntimeError) as error:
            result = {'error': {'message': str(error), 'status': 503}}
        responses.append({'id': request['id'], **result})
        st.session_state['hse_responses'] = responses[-2:]
        st.session_state['hse_processed'] = (st.session_state.get('hse_processed', []) + [request['id']])[-512:]
        st.rerun()
except Exception:
    stop_error('Piattaforma non disponibile: verificare il runtime PHP e il database esterno. Nessun dato viene archiviato sul disco effimero.')
