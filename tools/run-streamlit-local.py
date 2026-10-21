"""Local QA only; secrets read from ignored test config, never committed."""
import json
import os
from pathlib import Path
import subprocess
import sys
root=Path(__file__).resolve().parents[1]
env=dict(os.environ,**json.loads((Path(os.environ.get('HSE_QA_DIR', root/'.local'))/'streamlit-test-env.json').read_text()))
raise SystemExit(subprocess.call([sys.executable,'-m','streamlit','run',str(root/'app.py'),'--server.port=8505','--server.address=127.0.0.1','--browser.gatherUsageStats=false'],env=env,cwd=root))
