"""Native account, password, rate limit and revocation tests on external DB."""
import json
import os
from pathlib import Path
import secrets
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));os.environ.update(json.loads((Path(os.environ.get('HSE_QA_DIR', ROOT/'.local'))/'streamlit-test-env.json').read_text()))
from streamlit_app import database
c=json.loads(os.environ['HSE_DATABASE']);auth=json.loads(os.environ['HSE_AUTH']);database.initialize(c,auth)
admin=database.authenticate(c,auth['bootstrap_username'],auth['bootstrap_password']);assert admin
username='security-'+secrets.token_hex(6);password=secrets.token_urlsafe(24)
database.manage_users(c,admin,create={'username':username,'display_name':'Security QA','password':password})
user=database.authenticate(c,username,password);assert user and not user['is_admin'];version=user['token_version'];new=secrets.token_urlsafe(24)
assert database.change_password(c,user,password,new)==version+1
assert not database.authenticate(c,username,password)
assert database.authenticate(c,username,new)['token_version']==version+1
reset=secrets.token_urlsafe(24);database.manage_users(c,admin,update={'id':user['id'],'password':reset})
assert database.get_user(c,user['id'])['token_version']==version+2
assert not database.authenticate(c,username,new)
assert database.authenticate(c,username,reset)
for _ in range(5):assert not database.authenticate(c,username,'bad password')
assert not database.authenticate(c,username,reset),'Rate limiting not enforced'
database.manage_users(c,admin,update={'id':user['id'],'active':False,'is_admin':False})
assert database.get_user(c,user['id']) is None
try:database.manage_users(c,user,create={'username':'forged-admin','display_name':'Denied','password':reset})
except PermissionError:pass
else:raise AssertionError('Disabled user promoted account')
with database.connection(c) as db,db.cursor() as cur:
    cur.execute(f'SELECT password_hash FROM {c["prefix"]}users WHERE id=%s',(user['id'],));stored=cur.fetchone()['password_hash'];assert stored.startswith('pbkdf2_sha256$600000$') and reset not in stored
report={'native_accounts':True,'pbkdf2_600000':True,'own_password_change':True,'admin_password_reset':True,'session_version_revocation':True,'five_failures_lock_account':True,'disabled_account_rejected':True,'privilege_escalation_rejected':True}
(ROOT/'tests/artifacts/streamlit-auth.json').write_text(json.dumps(report,indent=2));print('PASS native accounts, PBKDF2, password change/reset, session revocation versions, rate limiting and disabled-user rejection')
# Prepare actual existing native actors for role browser checks.
ids=json.loads((Path(os.environ.get('HSE_QA_DIR', ROOT/'.local'))/'streamlit-test-ids.json').read_text());creds={}
for role,uid in ids['role_users'].items():
    p=secrets.token_urlsafe(24);database.manage_users(c,admin,update={'id':uid,'password':p});row=database.get_user(c,uid);creds[role]={'username':row['username'],'password':p}
p=Path(os.environ.get('HSE_QA_DIR', ROOT/'.local'))/'streamlit-role-auth.json';p.write_text(json.dumps(creds));p.chmod(0o600)
