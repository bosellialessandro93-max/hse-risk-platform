"""Reproducible PostgreSQL suite. Requires HSE_TEST_DATABASE_URL for a dedicated QA DB."""
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from streamlit_app.database import validated_config

url = os.environ.get('HSE_TEST_DATABASE_URL')
if not url:
    raise SystemExit('Impostare HSE_TEST_DATABASE_URL per un database PostgreSQL dedicato al collaudo (mai produzione).')
config = validated_config({'url':url, 'prefix':'qa_' + secrets.token_hex(4) + '_'})
qa = ROOT/'.local/streamlit-postgres-qa'
qa.mkdir(parents=True, exist_ok=True)
auth = {'mode':'password', 'bootstrap_username':'streamlit-admin', 'bootstrap_password':secrets.token_urlsafe(30)}
env = {'HSE_DATABASE':json.dumps(config), 'HSE_AUTH':json.dumps(auth)}
for key in ('HSE_PHP_COMMAND','HSE_RUNNER_PATH'):
    if key in os.environ:
        env[key] = os.environ[key]
f = qa/'streamlit-test-env.json'
f.write_text(json.dumps(env));f.chmod(0o600)
(ROOT/'tests/artifacts').mkdir(exist_ok=True)
php = json.loads(env.get('HSE_PHP_COMMAND','["php"]'))
version = subprocess.check_output(php+['-r','echo "PHP ".PHP_VERSION;'], text=True).strip()
child_env = dict(os.environ, HSE_QA_DIR=str(qa), HSE_QA_RUNTIME=version)
for test in ('configuration.py','backend.py','auth.py','postgres.py','session_isolation.py'):
    subprocess.run([sys.executable,str(ROOT/'tests/streamlit'/test)],env=child_env,cwd=ROOT,check=True)
print('PASS PostgreSQL suite; native browser QA config saved in ignored .local/streamlit-postgres-qa')
