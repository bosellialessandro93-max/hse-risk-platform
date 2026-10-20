"""Independent golden cases run the supplied Python functions against the PHP port."""
import copy, importlib.util, json, math, pathlib, random, subprocess, os
root=pathlib.Path(__file__).resolve().parents[1]
container=os.environ.get('HSE_TEST_CONTAINER','hse-wp')
php_version=subprocess.check_output(['docker','exec',container,'php','-r','echo PHP_VERSION;'],text=True).strip()
if os.environ.get('HSE_EXPECT_PHP'):assert php_version==os.environ['HSE_EXPECT_PHP'],php_version
print('Runtime PHP effettivo:',php_version)
spec=importlib.util.spec_from_file_location('original',root/'tests/reference/model_2_0_0.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
rng=random.Random(2000);cases=[]
for i in range(350):
 d=m.default_data();d.update(activities=rng.sample(list(m.ACTIVITY),rng.randint(1,10)),fase=rng.choice(list(m.PHASE_THEMES)),app=rng.randint(0,200),sub=rng.randint(0,200),hse_coverage=rng.uniform(0,100),inspections=rng.randint(0,50),inspection_target=rng.randint(1,100),stop_positive=rng.randint(0,15),stop_negative=rng.randint(0,15),interference_level=rng.randint(1,10),imminent_danger=i%13==0,hours=rng.choice([None,100,10000,1000000]),days=rng.choice([None,1,20,31]),workers=rng.choice([None,1,50,300]))
 for field in ['nc_items','crit_items']:
  d[field]=[dict(theme=rng.choice(m.THEMES),severity=rng.choice(list(m.SEVERITY)),status=rng.choice(list(m.STATUS)),late=bool(rng.getrandbits(1)),repeat=bool(rng.getrandbits(1))) for _ in range(rng.randint(0,15))]
 d['awareness']=[dict(theme=t,count=rng.randint(1,10),coverage=rng.choice([None,0,50,100])) for t in rng.sample(m.THEMES,rng.randint(0,len(m.THEMES)))];cases.append(d)
for count in [0,1,2]:
 d=m.default_data();d['nc_items']=[dict(theme='elettrico',severity='alta',status='Aperta',late=False,repeat=False)]*count;cases.append(d)
for d in [dict(m.default_data(),hours=None,days=None,workers=None),dict(m.default_data(),hours=None,days=20,workers=100),dict(m.default_data(),hours=None,days=None,workers=100),dict(m.default_data(),hours=4000,days=20,workers=100)]:cases.append(d)
subprocess.run(['docker','cp',str(root/'hse-risk-platform/includes/risk.php'),container+':/tmp/hse-risk.php'],check=True,capture_output=True)
subprocess.run(['docker','cp',str(root/'hse-risk-platform/includes/risk-catalog.json'),container+':/tmp/risk-catalog.json'],check=True,capture_output=True)
runner="<?php define('ABSPATH','/tmp/');require '/tmp/hse-risk.php';$d=json_decode(stream_get_contents(STDIN),true);echo json_encode(array_map(function($r){$v=HSE_Risk::calculate($r);$v['scenarios']=HSE_Risk::scenarios($r,$v);return $v;},$d),JSON_UNESCAPED_UNICODE);"
pathlib.Path('/tmp/hse-parity.php').write_text(runner)
subprocess.run(['docker','cp','/tmp/hse-parity.php',container+':/tmp/hse-parity.php'],check=True,capture_output=True)
p=subprocess.run(['docker','exec','-i',container,'php','/tmp/hse-parity.php'],input=json.dumps(cases),text=True,capture_output=True,check=True)
actual=json.loads(p.stdout)
keys=['version','score','level','raw','floor','floor_reason','drivers','awareness_details','awareness_bonus','needs','reasons','context_score','context_target','context_basis','missing']
def eq(a,b,path):
 if isinstance(a,(int,float)) and isinstance(b,(int,float)):assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-8),(path,a,b)
 elif isinstance(a,dict):
  assert a.keys()==b.keys(),(path,a,b)
  for k in a:eq(a[k],b[k],path+'/'+k)
 elif isinstance(a,list):
  assert len(a)==len(b),(path,a,b)
  for i,(x,y) in enumerate(zip(a,b)):eq(x,y,path+'/'+str(i))
 else:assert a==b,(path,a,b)
for i,(d,r) in enumerate(zip(cases,actual)):
 expected=m.calculate_risk(d)
 for k in keys:eq(expected[k],r[k],str(i)+'/'+k)
 eq(m.simulations(d,expected),r['scenarios'],str(i)+'/scenarios')
 assert math.isclose(sum(x['Contributo'] for x in r['drivers']),r['base'],abs_tol=1e-10)
 assert 0<=r['base']<=100
 if d['imminent_danger']:assert r['base']>=81
assert actual[351]['floor']==61 and actual[352]['floor']==81
print(f'PASS {len(cases)} Python/PHP parity cases; every component, bonus, floor, context and reconciliation')
# Classification must use unrounded values at every band edge.
cmd="require '/tmp/hse-risk.php';foreach([0,20,20.00001,40,40.00001,60,60.00001,80,80.00001,100] as $x)echo HSE_Risk::level($x).'|';"
bands=subprocess.check_output(['docker','exec',container,'php','-r',"define('ABSPATH','/tmp/');"+cmd],text=True)
assert bands=='Basso|Basso|Medio basso|Medio basso|Medio|Medio|Alto|Alto|Critico|Critico|'
print('PASS exact and adjacent classification boundaries')
