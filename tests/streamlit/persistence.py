"""Snapshot/verify external durable storage across a complete Streamlit process restart."""
import base64
import datetime
import hashlib
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));os.environ.update(json.loads((Path(os.environ.get('HSE_QA_DIR', ROOT/'.local'))/'streamlit-test-env.json').read_text()))
from streamlit_app.database import connection
config=json.loads(os.environ['HSE_DATABASE']);report={}
def encode(value):
    if isinstance(value,bytes):return base64.b64encode(value).decode()
    if isinstance(value,(datetime.datetime,datetime.date)):return value.isoformat()
    raise TypeError(type(value).__name__)
with connection(config) as db,db.cursor() as cur:
    for suffix,primary in {'hse_records':'id','hse_revisions':'id','hse_requests':'request_key','hse_assets':'id','users':'id','options':'name'}.items():
        cur.execute('SELECT * FROM '+config['prefix']+suffix+' ORDER BY '+primary);rows=cur.fetchall();serialized=json.dumps(rows,sort_keys=True,default=encode)
        report[suffix]={'rows':len(rows),'sha256':hashlib.sha256(serialized.encode()).hexdigest()}
p=Path(os.environ.get('HSE_QA_DIR', ROOT/'.local'))/'streamlit-restart-before.json'
if '--before' in sys.argv:p.write_text(json.dumps(report));print('Recorded external storage baseline before process termination')
else:
    assert report==json.loads(p.read_text()),'Durable records changed across restart'
    (ROOT/'tests/artifacts/streamlit-persistence.json').write_text(json.dumps({'process_restart':True,'external_tables':report,'all_identical':True},indent=2));print('PASS process restart: six external tables, records, revisions, requests, binaries, accounts and options identical')
