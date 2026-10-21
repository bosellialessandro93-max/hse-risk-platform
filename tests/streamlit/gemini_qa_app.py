import io,json,os,runpy,sys
from pathlib import Path
from unittest.mock import patch
if os.environ.get('HSE_GEMINI_QA')!='1': raise RuntimeError('QA-only launcher required')
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
from streamlit_app import gemini
calls=root/'.local/gemini-qa-call-count.txt'
def fake(req,timeout):
 if not req.full_url.startswith('https://generativelanguage.googleapis.com/'):
  raise AssertionError('Unexpected external request')
 calls.write_text(str(int(calls.read_text() if calls.exists() else '0')+1))
 return io.BytesIO(json.dumps({'candidates':[{'content':{'parts':[{'text':'Analisi sintetica di collaudo. Verificare le evidenze prima di agire.'}]}}]}).encode())
with patch.object(gemini.request,'urlopen',side_effect=fake):
 runpy.run_path(str(root/'app.py'),run_name='__main__')
