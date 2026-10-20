"""Linux/Docker QA setup. Creates only a separate synthetic DB and copies PHP modules to /tmp."""
import argparse
import json
from pathlib import Path
import secrets
import subprocess

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--db-container',default='hse-db');parser.add_argument('--php-container',default='hse-wp-php80');args=parser.parse_args()
password=secrets.token_hex(24);admin=secrets.token_urlsafe(24)
sql=f"CREATE DATABASE IF NOT EXISTS hse_streamlit_test CHARACTER SET utf8mb4; CREATE USER IF NOT EXISTS 'hse_st_test'@'%' IDENTIFIED BY '{password}'; ALTER USER 'hse_st_test'@'%' IDENTIFIED BY '{password}'; GRANT ALL ON hse_streamlit_test.* TO 'hse_st_test'@'%';"
subprocess.run(['docker','exec','-i',args.db_container,'mariadb'],input=sql,text=True,check=True,capture_output=True)
host=subprocess.check_output(['docker','inspect',args.db_container,'--format','{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'],text=True).strip()
env={'HSE_DATABASE':json.dumps({'host':host,'port':3306,'name':'hse_streamlit_test','user':'hse_st_test','password':password,'prefix':'st_','tls':False}),
     'HSE_AUTH':json.dumps({'mode':'password','bootstrap_username':'streamlit-admin','bootstrap_password':admin}),
     'HSE_PHP_COMMAND':json.dumps(['docker','exec','-i','-e','HSE_DATABASE',args.php_container,'php']),
     'HSE_RUNNER_PATH':'/tmp/hse-streamlit/streamlit_app/runtime/runner.php'}
local=ROOT/'.local';local.mkdir(exist_ok=True);path=local/'streamlit-test-env.json'
# Existing test accounts keep their passwords; bootstrap secret is used only on an empty account table.
if path.exists():
    old=json.loads(path.read_text());env['HSE_AUTH']=old['HSE_AUTH']
path.write_text(json.dumps(env));path.chmod(0o600)
subprocess.run(['docker','exec',args.php_container,'mkdir','-p','/tmp/hse-streamlit/streamlit_app','/tmp/hse-streamlit/hse-risk-platform','/tmp/hse-streamlit/tests/streamlit'],check=True)
for source,dest in [('streamlit_app/runtime','streamlit_app/'),('hse-risk-platform/includes','hse-risk-platform/'),('tests/streamlit/runtime.php','tests/streamlit/runtime.php')]:
    subprocess.run(['docker','cp',str(ROOT/source),args.php_container+':/tmp/hse-streamlit/'+dest],check=True)
print('Prepared isolated MySQL QA account and independent PHP runtime; secrets saved only in ignored .local/streamlit-test-env.json')
