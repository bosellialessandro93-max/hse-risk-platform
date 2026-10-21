"""Real local PostgreSQL/PHP checks for weekly periods and embedded KMZ landscape."""
import base64,io,json,os,struct,sys,uuid,zipfile,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
qa=Path(os.environ.get('HSE_QA_DIR',ROOT/'.local/streamlit-postgres-qa'))
os.environ.update(json.loads((qa/'streamlit-test-env.json').read_text()))
from streamlit_app import database
from streamlit_app.gateway import invoke
config=json.loads(os.environ['HSE_DATABASE']);auth=json.loads(os.environ['HSE_AUTH'])
assert config['host'] in ('127.0.0.1','localhost'), 'Local QA only'
admin=database.authenticate(config,auth['bootstrap_username'],auth['bootstrap_password']);assert admin
ids=json.loads((qa/'streamlit-test-ids.json').read_text());sid=ids['site_id']
def api(path,data=None,method='GET',status=200,files=None,form=None):
 result=invoke(config,admin,request=dict(path=path,method=method,data=data,files=files or {},form=form or {}))
 if status!=200:
  assert result.get('error',{}).get('status')==status,(path,result);return result['error']
 assert 'error' not in result,(path,result);return result['data']
def create(kind,d):return api(kind,{**d,'request_id':str(uuid.uuid4())},'POST')
base=dict(site_id=sid,week='2026-09-28',phase='costruzione',activities=['elettrici'],contractors=1,subcontractors=0,coverage=80,interference=3,inspections=2,days=7)
calc=api('risk/calculate',base,'POST');assert calc['period_end']=='2026-10-04' and calc['month']=='2026-09'
for overrides in [dict(week='2026-09-29'),dict(week='2099-01-05'),dict(days=8),dict(week='',month='2026-09')]:api('risk/calculate',{**base,**overrides},'POST',422)
api('risk/save',{**calc,'week':'2026-10-05','request_id':str(uuid.uuid4())},'POST',409)
records=[]
for week in ['2026-09-28','2026-09-21','2025-12-29']:
 c=api('risk/calculate',{**base,'week':week},'POST');records.append(api('risk/save',{**c,'request_id':str(uuid.uuid4())},'POST'))
assert records[-1]['period_end']=='2026-01-04'
history=api('risk/history?site_id='+sid);assert all(any(r['id']==record['id'] for r in history) for record in records)
event=dict(site_id=sid,event_date='2026-10-05',channel='formal',topic='elettrico',severity='Low',state='Open')
e=create('events',event);api('risk/calculate',{**base,'event_ids':[e['id']]},'POST',422)
e=create('events',{**event,'event_date':'2026-09-30'});assert api('risk/calculate',{**base,'event_ids':[e['id']]},'POST')['event_snapshots'][0]['id']==e['id']
legacy_event=create('events',{**event,'event_date':'','month':'2026-09'});api('risk/calculate',{**base,'event_ids':[legacy_event['id']]},'POST',422)
api('risk/comparison?site_id='+sid+'&week=2026-09-28');api('risk/comparison?site_id='+sid+'&week=2026-10-19',status=422)
# Legacy publications are seeded only into the dedicated local QA database to simulate pre-upgrade data.
legacy={**records[0],'id':str(uuid.uuid4()),'month':'2026-08','period_type':'month'}
for key in ['week','period_end']:legacy.pop(key,None)
legacy['policy']={**legacy['policy'],'version':'2.0.0-target-4'}
with database.connection(config) as db:
 with db.cursor() as cursor:
  table=config['prefix']+'hse_records';revisions=config['prefix']+'hse_revisions'
  cursor.execute(f'INSERT INTO {table} (id,kind,site_id,company_id,version,author_id,created_at,updated_at,payload) VALUES (%s,%s,%s,%s,1,%s,NOW(),NOW(),%s)',(legacy['id'],'assessments',sid,'',admin['id'],json.dumps(legacy)))
  cursor.execute(f'INSERT INTO {revisions} (record_id,version,payload,created_at,author_id) VALUES (%s,1,%s,NOW(),%s)',(legacy['id'],json.dumps(legacy),admin['id']))
 db.commit()
assert any(r['id']==legacy['id'] and not r.get('week') for r in api('risk/history?site_id='+sid))
snapshot=create('exports',dict(site_id=sid,source_id=legacy['id'],source_version=1,format='json'));assert snapshot['record']['result']==legacy['result']
restored=api('backup',dict(site_id=sid,type='assessments',backup=api('backup?site_id='+sid+'&type=assessments'),confirm=True,request_id=str(uuid.uuid4())),'POST');assert restored
# Build a small real raster fixture, with a georeferenced overlay and a blocked remote one.
def chunk(kind,data):return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',64,64,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\x00'+bytes([20,160,100])*64)*64))+chunk(b'IEND',b'')
overlay='<GroundOverlay><name>Paesaggio QA</name><Icon><href>images/landscape.png</href></Icon><LatLonBox><north>42</north><south>41</south><east>13</east><west>12</west><rotation>0</rotation></LatLonBox></GroundOverlay>'
point='<Placemark><name>Punto QA</name><Point><coordinates>12.5,41.5</coordinates></Point></Placemark>'
for name,features in [('landscape-qa.kmz',point),('landscape-only-qa.kmz','')]:
 stream=io.BytesIO()
 with zipfile.ZipFile(stream,'w',zipfile.ZIP_DEFLATED) as z:
  z.writestr('doc.kml','<kml><Document>'+features+overlay+overlay.replace('images/landscape.png','https://example.invalid/secret.png')+'</Document></kml>');z.writestr('images/landscape.png',png)
 (ROOT/'.local'/name).write_bytes(stream.getvalue())
 imported=api('maps/import',method='POST',files={'file':dict(name=name,base64=base64.b64encode(stream.getvalue()).decode())},form=dict(site_id=sid))
 assert len(imported['landscape'])==1 and any('remoto' in w for w in imported['warnings'])
 saved=create('maps',dict(site_id=sid,title='Paesaggio QA',geojson=imported['geojson'],landscape=imported['landscape'],map_layout='landscape',signs=[]))
 read=api('maps/'+saved['id']);assert read['map_layout']=='landscape' and read['landscape']==imported['landscape']
 api('maps',dict(site_id=sid,title='Bad',geojson=imported['geojson'],landscape=[{**imported['landscape'][0],'chunks':[base64.b64encode(b'<svg onload="x"/>').decode()]}],request_id=str(uuid.uuid4())),'POST',422)
ids.update(landscape_id=saved['id'],weekly_id=records[0]['id'],legacy_id=legacy['id']);(qa/'weekly-feature-ids.json').write_text(json.dumps(ids))
print('PASS weekly boundaries, cross-month/year, days, event dates, hash guard, distinct history, comparison, legacy preservation/restore, KMZ embedded landscape/overlay-only/persistence and unsafe image rejection')
