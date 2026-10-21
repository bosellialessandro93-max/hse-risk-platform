<?php
/** Run only against a dedicated QA database via HSE_DATABASE, never production. */
require dirname(__DIR__,2).'/streamlit_app/runtime/compatibility.php';
require dirname(__DIR__,2).'/streamlit_app/runtime/postgres.php';
define('ABSPATH',dirname(__DIR__,2).'/streamlit_app/runtime/');
require dirname(__DIR__,2).'/hse-risk-platform/includes/store.php';
$config=json_decode(getenv('HSE_DATABASE'),true,512,JSON_THROW_ON_ERROR);
$GLOBALS['hse_actor']=['id'=>1,'is_admin'=>true];$wpdb=new HSE_PG_DB($config);
HSE_Store::activate();HSE_Store::activate();
function check_pg($value,$message){if(!$value)throw new RuntimeException($message);}
// Complete byte spectrum, SQL-looking text and Unicode must survive unchanged.
$binary=implode('',array_map('chr',range(0,255)));$id=wp_generate_uuid4();$now=gmdate('Y-m-d H:i:s');
check_pg($wpdb->insert(HSE_Store::table('assets'),['id'=>$id,'site_id'=>wp_generate_uuid4(),'company_id'=>'','author_id'=>1,'name'=>"apostrofo ' e città",'mime'=>'application/octet-stream','digest'=>hash('sha256',$binary),'content'=>$binary,'created_at'=>$now])===1,'Binary insert');
$asset=$wpdb->get_row($wpdb->prepare('SELECT * FROM '.HSE_Store::table('assets').' WHERE id=%s',$id));
check_pg($asset['content']===$binary&&$asset['name']==="apostrofo ' e città",'Bytea roundtrip');
$value=['text'=>"è \\ ' ON DUPLICATE KEY UPDATE value=VALUES(value)"];
update_option('pg_test_option',$value);check_pg(get_option('pg_test_option')===$value,'JSON SQL-like text');
update_option('pg_test_option',['updated'=>true]);check_pg(get_option('pg_test_option')===['updated'=>true],'Options upsert');
$id=wp_generate_uuid4();$rid=wp_generate_uuid4();
try{HSE_Store::atomic($rid,'rollback-proof',function()use($id){HSE_Store::save('observations',['site_id'=>'rollback-proof'],$id,0,true);throw new HSE_Fault('Deliberate rollback',422);});throw new RuntimeException('Rollback not triggered');}
catch(HSE_Fault $e){check_pg($e->getMessage()==='Deliberate rollback','Wrong exception');}
check_pg((int)$wpdb->get_var($wpdb->prepare('SELECT count(*) FROM '.HSE_Store::table().' WHERE id=%s',$id))===0,'Record rollback');
check_pg((int)$wpdb->get_var($wpdb->prepare('SELECT count(*) FROM '.HSE_Store::table('revisions').' WHERE record_id=%s',$id))===0,'Revision rollback');
$key=hash('sha256','1:'.$rid);check_pg((int)$wpdb->get_var($wpdb->prepare('SELECT count(*) FROM '.HSE_Store::table('requests').' WHERE request_key=%s',$key))===0,'Request rollback');
echo 'PASS PostgreSQL repeated schema, bytea/NUL/Unicode, options upsert, record/revision/request rollback'.PHP_EOL;
