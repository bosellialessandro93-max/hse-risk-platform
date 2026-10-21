import io,json,os,runpy,sys
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
if os.environ.get('HSE_GEMINI_QA')!='1': raise RuntimeError('QA-only launcher required')
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root))
from streamlit_app import gemini
calls=root/'.local/gemini-qa-call-count.txt'
def fake(req,timeout):
 if not req.full_url.startswith('https://generativelanguage.googleapis.com/'):
  raise AssertionError('Unexpected external request')
 calls.write_text(str(int(calls.read_text() if calls.exists() else '0')+1))
 mode=root/'.local/gemini-qa-error-code.txt'
 if mode.exists() and mode.read_text().strip()=='429':
  raise HTTPError(req.full_url,429,'private-provider-error',{},io.BytesIO(json.dumps({'error':{'message':'qa-synthetic-key-never-a-real-credential private-provider-error','status':'RESOURCE_EXHAUSTED'}}).encode()))
 result={'supportedGenerationMethods':['generateContent']} if req.get_method()=='GET' else {'candidates':[{'content':{'parts':[{'text':'Analisi sintetica di collaudo. Verificare le evidenze prima di agire.'}]}}]}
 return io.BytesIO(json.dumps(result).encode())
with patch.object(gemini.request,'urlopen',side_effect=fake):
 runpy.run_path(str(root/'app.py'),run_name='__main__')
