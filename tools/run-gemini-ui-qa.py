"""Start port 8506 with synthetic Secrets and a mocked provider, never real Gemini."""
import json
import os
from pathlib import Path
import subprocess
import sys
root=Path(__file__).resolve().parents[1]
qa=Path(os.environ.get('HSE_QA_DIR',root/'.local/streamlit-postgres-qa'))
env=dict(os.environ,**json.loads((qa/'streamlit-test-env.json').read_text()),HSE_GEMINI_QA='1')
config=json.loads(env['HSE_DATABASE'])
if config.get('host') not in ('127.0.0.1','localhost'):
    raise SystemExit('This UI test requires the dedicated local QA database.')
secrets=root/'.local/gemini-ui-qa-secrets.toml'
secrets.write_text('"Gemini API Key" = "qa-synthetic-key-never-a-real-credential"\n[gemini]\nenabled = true\nprocessing_authorized = false\nallow_confidential_data = false\n')
secrets.chmod(0o600)
raise SystemExit(subprocess.call([sys.executable,'-m','streamlit','run',str(root/'tests/streamlit/gemini_qa_app.py'),'--server.port=8506','--server.address=127.0.0.1','--browser.gatherUsageStats=false','--secrets.files',str(secrets)],env=env,cwd=root))
