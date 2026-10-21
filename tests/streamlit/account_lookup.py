"""QA-only lookup, returns an ID without displaying credentials."""
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from streamlit_app.database import connection
qa=Path(os.environ.get('HSE_QA_DIR',ROOT/'.local'))
config=json.loads(json.loads((qa/'streamlit-test-env.json').read_text())['HSE_DATABASE'])
with connection(config) as db,db.cursor() as cur:
    cur.execute(f'SELECT id FROM {config["prefix"]}users WHERE username=%s',(sys.argv[1],));row=cur.fetchone();assert row;print(row['id'])
