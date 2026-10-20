"""Run after preparing the test DB and starting tools/run-streamlit-local.py on port 8505."""
from pathlib import Path
import os
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
env=dict(os.environ,HSE_QA_PYTHON=sys.executable)
for filename in ['backend.py','auth.py','session_isolation.py']:
    subprocess.run([sys.executable,str(ROOT/'tests/streamlit'/filename)],cwd=ROOT,env=env,check=True)
for filename in ['roles.mjs','browser.mjs','accounts-ui.mjs','smoke.mjs']:
    subprocess.run(['node',str(ROOT/'tests/streamlit'/filename)],cwd=ROOT,env=env,check=True)
subprocess.run([sys.executable,str(ROOT/'tests/streamlit/validate_exports.py')],cwd=ROOT,env=env,check=True)
print('PASS Streamlit integration/browser/auth/export suite')
