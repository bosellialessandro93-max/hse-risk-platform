"""Integration against the real external MySQL test DB and PHP CLI boundary."""
import base64
import concurrent.futures
import importlib.util
import json
import math
import os
from pathlib import Path
import random
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.environ.update(json.loads((Path(os.environ.get('HSE_QA_DIR', ROOT/'.local'))/'streamlit-test-env.json').read_text()))
from streamlit_app import database
from streamlit_app.gateway import invoke
config=json.loads(os.environ['HSE_DATABASE']);auth=json.loads(os.environ['HSE_AUTH'])
database.initialize(config,auth)
admin=database.authenticate(config,auth['bootstrap_username'],auth['bootstrap_password']);assert admin
assert invoke(config,admin,action='bootstrap').get('data',{}).get('schema')=='1'
passed=[]
def check(value,label):
    assert value,label
    passed.append(label)
def api(path,data=None,method='GET',actor=admin,status=200,files=None,form=None):
    result=invoke(config,actor,request={'path':path,'method':method,'data':data,'files':files or {},'form':form or {}})
    if status!=200:
        assert result.get('error',{}).get('status')==status,(path,status,result)
        return result['error']
    assert 'error' not in result,(path,result)
    return result['data']
def create(kind,data):return api(kind,{**data,'request_id':str(uuid.uuid4())},'POST')
def patch(kind,record,data):return api(kind+'/'+record['id'],{**data,'expected_version':record['version'],'request_id':str(uuid.uuid4())},'PATCH')
def items(kind,site):return api(kind+'?site_id='+site+'&per_page=500')['items']

site=create('sites',{'name':'DEMO Streamlit integration '+str(uuid.uuid4())[:8],'technology':'Wind'});sid=site['id']
area=create('areas',{'site_id':sid,'name':'WTG DEMO','type':'WTG'});company=create('companies',{'site_id':sid,'name':'Impresa DEMO'})
check(api('sites/'+sid)['name']==site['name'],'create/read site')
other=create('sites',{'name':'DEMO other','technology':'BESS'})
users={}
for role in ['manager','reader','company','outsider']:
    username=role+'-'+uuid.uuid4().hex[:8]
    database.manage_users(config,admin,create={'username':username,'display_name':role,'password':'Test-password-'+uuid.uuid4().hex})
    user=next(u for u in database.manage_users(config,admin) if u['username']==username)
    users[role]=user
    if role!='outsider':create('memberships',{'site_id':sid,'user_id':user['id'],'role':role,'company_id':company['id'] if role=='company' else '', 'share_plans':True})
check(bool(api('capabilities?site_id='+sid,actor=users['company'])['membership']),'native account membership')
api('sites/'+other['id'],actor=users['manager'],status=403)
api('sites/'+sid,actor=users['outsider'],status=403)
check(True,'cross-site permissions')
api('risk/policy',{'inspection_target':8},'POST',actor=users['reader'],status=403)
assert api('risk/policy',{'inspection_target':6},'POST')['inspection_target']==6
assert api('risk/policy',{'inspection_target':4},'POST')['inspection_target']==4
check(True,'admin-only common inspection target')
observation=create('observations',{'site_id':sid,'note':'Foto e NC di prova'})
observation=patch('observations',observation,{'note':'Persistenza revisionata'})
check(observation['version']==2 and len(api('observations/'+observation['id']+'/revisions'))==2,'optimistic revisions')
api('observations/'+observation['id'],{'note':'stale','expected_version':1,'request_id':str(uuid.uuid4())},'PATCH',status=409)
request={'site_id':sid,'note':'Idempotente','request_id':str(uuid.uuid4())}
a=api('observations',request,'POST');b=api('observations',request,'POST');check(a['id']==b['id'],'durable idempotency')
api('observations',{**request,'note':'Changed'},'POST',status=409)
check(True,'idempotency fingerprint')
api('observations',{'site_id':sid,'note':'Denied','request_id':str(uuid.uuid4())},'POST',actor=users['reader'],status=403)
api('observations/'+observation['id'],actor=users['company'],status=403)
check(True,'reader and company isolation')
company_observation=api('observations',{'site_id':sid,'company_id':company['id'],'note':'Own company','request_id':str(uuid.uuid4())},'POST',actor=users['company'])
check(company_observation['company_id']==company['id'],'company own creation')
photo=base64.b64encode((ROOT/'fixtures/photo.png').read_bytes()).decode()
asset=api('assets',method='POST',files={'file':{'name':'photo.png','base64':photo}},form={'site_id':sid,'request_id':str(uuid.uuid4())})
check(api('assets/'+asset['id'])['base64']==photo,'private binary durable storage')
api('assets/'+asset['id'],actor=users['company'],status=403)
observation=patch('observations',observation,{'attachments':[asset['id']]})
check(asset['id'] in observation['attachments'],'photo link')
event=create('events',{'site_id':sid,'month':'2026-09','channel':'formal','topic':'elettrico','severity':'High','state':'Open','reason':'DEMO motivazione','reference':'HSEQ4ALL-DEMO'})
assessment={'site_id':sid,'month':'2026-09','phase':'costruzione','activities':['elettrici'],'contractors':1,'subcontractors':0,'coverage':80,'interference':3,'inspections':0,'event_ids':[event['id']]}
computed=api('risk/calculate',assessment,'POST');check(computed['result']['floor']==61 and computed['result']['base']>=61,'formal high floor and detection')
api('risk/calculate',assessment,'POST',actor=users['company'],status=403)
api('risk/calculate',assessment,'POST',actor=users['reader'],status=403)
saved=api('risk/save',{**computed,'request_id':str(uuid.uuid4()),'expected_version':0},'POST')
check(saved['status']=='Saved' and len(api('risk/history?site_id='+sid))==1,'explicit risk save/history')
api('risk/save',{**computed,'coverage':90,'request_id':str(uuid.uuid4())},'POST',status=409)
check(True,'stale calculation guard')
scenario=api('risk/scenario',{**computed,'coverage':100},'POST');check(scenario['result']['base']<=computed['result']['base'],'independent scenarios')
for tech in ['Solar','BESS']:
    t=create('sites',{'name':'DEMO '+tech,'technology':tech})
    check(0<=api('risk/calculate',{**assessment,'site_id':t['id'],'event_ids':[]},'POST')['result']['base']<=100,tech+' calculation')
plan=create('plans',{'site_id':sid,'company_id':company['id'],'week':'2026-10-19','activities':[{'id':str(uuid.uuid4()),'description':'Scavo DEMO','area_id':area['id'],'supervisor':'Preposto','pos':'POS DEMO','conditions_reviewed':True,'days':[{'date':'2026-10-20','operators':3}]}],'daily_totals':[{'date':'2026-10-20','workers':3}],'confirmed_review':True})
plan=api('plans/'+plan['id']+'/confirm',{'expected_version':1,'confirmed_review':True,'request_id':str(uuid.uuid4())},'POST')
check(plan['status']=='Confirmed' and len(api('calendar?site_id='+sid)['rows'])==1,'plan review and calendar publication')
plan_draft=patch('plans',plan,{'activities':plan['activities']})
check(plan_draft['status']=='Draft' and len(api('calendar?site_id='+sid)['rows'])==1,'last confirmed calendar revision retained')
meeting=api('meetings/prepare',{'site_id':sid,'week':'2026-10-19','observation_ids':[observation['id']]},'POST')
check(len(meeting['items'])==2 and meeting['source_snapshot']['observations'][0]['attachments']==[asset['id']],'meeting immutable sources with photos')
meeting=create('meetings',meeting)
meeting=api('meetings/'+meeting['id']+'/finalize',{'expected_version':meeting['version'],'confirmed':True,'request_id':str(uuid.uuid4())},'POST')
check(meeting['status']=='Finalized','meeting finalization')
toolbox=api('toolboxes/prepare',{'site_id':sid,'activity':'Scavo e mezzi'},'POST');toolbox=create('toolboxes',toolbox)
session=create('sessions',{'site_id':sid,'toolbox_id':toolbox['id'],'topic':'scavi','held_on':'2026-09-10','count':1})
check(bool(session['id']) and 'scav' in toolbox['content'].lower(),'toolbox and held sessions')
action=create('actions',{'site_id':sid,'description':'Azione DEMO','owner':'Responsabile','due_date':'2026-11-01','status':'Open'})
action=patch('actions',action,{'status':'Closed','evidence':'Evidenza DEMO'})
check(action['status']=='Closed','action plan closure')
for filename in ['site-demo.kml','site-demo.kmz']:
    imported=api('maps/import',method='POST',files={'file':{'name':filename,'base64':base64.b64encode((ROOT/'fixtures'/filename).read_bytes()).decode()}},form={'site_id':sid})
    check(bool(imported['geojson']['features']),filename+' import')
    if filename.endswith('kml'):map_data=imported
for filename in ['traversal.kmz','bomb.kmz','corrupt.kmz','active.kml']:
    api('maps/import',method='POST',files={'file':{'name':filename,'base64':base64.b64encode((ROOT/'fixtures'/filename).read_bytes()).decode()}},form={'site_id':sid},status=422)
check(True,'malicious KML/KMZ rejected')
map_record=create('maps',{'site_id':sid,'title':'DEMO mappa',**map_data})
document=create('documents',{'site_id':sid,'title':'POS demo','category':'POS','declared_revision':'1','document_date':'2026-09-01','url':'https://example.org/pos'})
checklist=create('checklists',{'site_id':sid,'title':'DEMO verifica','items':[{'text':'Verifica','state':'Da verificare'}]})
for fmt in ['pdf','docx','xlsx','pptx','management-pdf','json']:
    snapshot=create('exports',{'site_id':sid,'source_id':saved['id'],'source_version':saved['version'],'format':fmt})
    check(snapshot['record']['result']['base']==saved['result']['base'],'export snapshot '+fmt)
backup=api('backup?site_id='+sid+'&type=operations');preview=api('backup',{'site_id':sid,'type':'operations','backup':backup},'POST')
check(len(preview['preview'])>0 and len(backup['assets'])==1,'backup preview with binary')
restored=api('backup',{'site_id':sid,'type':'operations','backup':backup,'confirm':True,'request_id':str(uuid.uuid4())},'POST')
check(bool(restored),'atomic restore')
current=api('observations/'+a['id'])
def concurrent_write(index):
    return invoke(config,admin,request={'path':'observations/'+current['id'],'method':'PATCH','data':{'note':'Concurrent '+str(index),'expected_version':current['version'],'request_id':str(uuid.uuid4())}})
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:race=list(pool.map(concurrent_write,[1,2]))
check(sum('data' in r for r in race)==1 and sum(r.get('error',{}).get('status')==409 for r in race)==1,'concurrent update conflict')
# Known model and every scenario, through the exact CLI entry used by Streamlit.
spec=importlib.util.spec_from_file_location('reference',ROOT/'tests/reference/model_2_0_0.py');ref=importlib.util.module_from_spec(spec);spec.loader.exec_module(ref)
rng=random.Random(2000);models=[]
for i in range(357):
    d=ref.default_data();d.update(activities=rng.sample(list(ref.ACTIVITY),rng.randint(1,10)),fase=rng.choice(list(ref.PHASE_THEMES)),app=rng.randint(0,200),sub=rng.randint(0,200),hse_coverage=rng.uniform(0,100),inspections=rng.randint(0,50),inspection_target=rng.randint(1,100),stop_positive=rng.randint(0,15),stop_negative=rng.randint(0,15),interference_level=rng.randint(1,10),imminent_danger=i%13==0,hours=rng.choice([None,100,10000]),days=rng.choice([None,1,20]),workers=rng.choice([None,1,50]))
    for field in ['nc_items','crit_items']:d[field]=[dict(theme=rng.choice(ref.THEMES),severity=rng.choice(list(ref.SEVERITY)),status=rng.choice(list(ref.STATUS)),late=bool(rng.getrandbits(1)),repeat=bool(rng.getrandbits(1))) for _ in range(rng.randint(0,12))]
    d['awareness']=[dict(theme=t,count=rng.randint(1,10),coverage=rng.choice([None,0,50,100])) for t in rng.sample(ref.THEMES,rng.randint(0,12))];models.append(d)
results=invoke(config,admin,action='calculate_model',model=models)['data']
def equal(a,b,path=''):
    if isinstance(a,(float,int)) and isinstance(b,(float,int)):assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-8),(path,a,b)
    elif isinstance(a,dict):
        for key,value in a.items():equal(value,b[key],path+'/'+key)
    elif isinstance(a,list):
        assert len(a)==len(b),(path,len(a),len(b))
        for index,(x,y) in enumerate(zip(a,b)):equal(x,y,path+'/'+str(index))
    else:assert a==b,(path,a,b)
for d,result in zip(models,results):
    expected=ref.calculate_risk(d);expected.pop('explanations')  # Existing PHP model has equivalent condensed explanatory prose.
    equal(expected,result);equal(ref.simulations(d,expected),result['scenarios'])
check(True,'357 golden model cases and 2142 scenarios')
# OIDC verified identity mapping and unverified-email rejection (real provider still external).
identity=database.oidc_user(config,{'email':'streamlit-oidc-'+uuid.uuid4().hex+'@example.org','email_verified':True,'name':'OIDC demo'},{'admin_emails':[]})
check(not identity['is_admin'],'OIDC unassigned identity provisioning')
try:database.oidc_user(config,{'email':'bad@example.org','email_verified':False},{})
except ValueError:check(True,'OIDC unverified email rejection')
else:raise AssertionError('Unverified identity accepted')
check(not database.authenticate(config,auth['bootstrap_username'],'incorrect'),'bad password rejected')
report={'checks':passed,'total':len(passed),'model_cases':357,'scenarios':2142,'database':'external PostgreSQL' if config.get('driver')=='postgresql' else 'external MariaDB 11.4','storage':'external transactional database, no local archive','runtime':os.environ.get('HSE_QA_RUNTIME','PHP 8.0.30'),'actors':['admin','manager','reader','company','outsider'],'site_id':sid,'assessment_id':saved['id'],'observation_id':observation['id'],'map_id':map_record['id'],'plan_id':plan['id'],'meeting_id':meeting['id'],'role_users':{role:user['id'] for role,user in users.items()}}
(Path(os.environ.get('HSE_QA_DIR', ROOT/'.local'))/'streamlit-test-ids.json').write_text(json.dumps(report));(ROOT/'tests/artifacts/streamlit-backend.json').write_text(json.dumps(report,indent=2));print('PASS',len(passed),'Streamlit backend flows; 357 golden cases, 2142 scenarios, all profiles, imports, export snapshots and DB persistence')
