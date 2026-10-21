"""Check Streamlit server state cannot carry private response caches between identities."""
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));os.environ.update(json.loads((Path(os.environ.get('HSE_QA_DIR', ROOT/'.local'))/'streamlit-test-env.json').read_text()))
from streamlit.testing.v1 import AppTest
from streamlit_app import database
c=json.loads(os.environ['HSE_DATABASE']);a=json.loads(os.environ['HSE_AUTH']);admin=database.authenticate(c,a['bootstrap_username'],a['bootstrap_password']);assert admin
app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30)
app.session_state['user_id']=admin['id'];app.session_state['login_version']=admin['token_version'];app.session_state['hse_owner']=-1;app.session_state['hse_responses']=[{'private_marker':'previous-user'}];app.session_state['hse_ai_text']='previous-user-text';app.run()
assert not app.exception
assert app.session_state['hse_owner']==admin['id'] and app.session_state['hse_responses']==[]
assert 'hse_ai_text' not in app.session_state
with database.connection(c) as db,db.cursor() as cur:
    cur.execute(f'SELECT id FROM {c["prefix"]}users WHERE active=0 LIMIT 1');disabled=cur.fetchone();assert disabled
app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30);app.session_state['user_id']=disabled['id'];app.session_state['hse_responses']=[{'private_marker':'disabled-user'}];app.run();assert not app.exception
try:app.session_state['hse_responses']
except KeyError:pass
else:raise AssertionError('Disabled identity response cache retained')
for key in ['HSE_DATABASE','HSE_AUTH']:os.environ.pop(key,None)
app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run();assert not app.exception and len(app.error)==1
report={'cross_identity_response_cache_cleared':True,'disabled_account_state_cleared':True,'missing_configuration_stops_without_local_archive':True}
(ROOT/'tests/artifacts/streamlit-session-isolation.json').write_text(json.dumps(report,indent=2));print('PASS Streamlit session isolation, deactivated identity cleanup and no local-storage fallback')
