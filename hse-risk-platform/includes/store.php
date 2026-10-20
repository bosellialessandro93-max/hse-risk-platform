<?php
if (!defined('ABSPATH')) exit;
class HSE_Fault extends RuntimeException {
 public int $status; public $details;
 function __construct($message,$status=422,$details=null){parent::__construct($message);$this->status=$status;$this->details=$details;}
}
class HSE_Store {
 static function table($suffix='records'){global $wpdb;return $wpdb->prefix.'hse_'.$suffix;}
 static function activate(){
  $missing=[];foreach(['mysqli','mbstring','fileinfo','simplexml','zip'] as $extension)if(!extension_loaded($extension))$missing[]=$extension;
  if(version_compare(PHP_VERSION,'8.0.30','<')||$missing){$message=version_compare(PHP_VERSION,'8.0.30','<')?'HSE Risk Platform richiede PHP 8.0.30 o successivo. ':'HSE Risk Platform: estensioni PHP mancanti: '.implode(', ',$missing).'. ';wp_die(esc_html($message.'Verificare i requisiti con il gestore hosting prima di attivare il plugin.'));}
  self::migrate();
 }
 static function migrate(){
  global $wpdb; require_once ABSPATH.'wp-admin/includes/upgrade.php';$c=$wpdb->get_charset_collate();
  dbDelta('CREATE TABLE '.self::table()." (
 id varchar(36) NOT NULL,
 kind varchar(32) NOT NULL,
 site_id varchar(36) NOT NULL DEFAULT '',
 company_id varchar(36) NOT NULL DEFAULT '',
 version bigint NOT NULL DEFAULT 1,
 author_id bigint NOT NULL,
 created_at datetime NOT NULL,
 updated_at datetime NOT NULL,
 payload longtext NOT NULL,
 PRIMARY KEY  (id),
 KEY scope (site_id,kind)
 ) ENGINE=InnoDB $c;");
  dbDelta('CREATE TABLE '.self::table('revisions')." (
 id bigint NOT NULL AUTO_INCREMENT,
 record_id varchar(36) NOT NULL,
 version bigint NOT NULL,
 payload longtext NOT NULL,
 created_at datetime NOT NULL,
 author_id bigint NOT NULL,
 PRIMARY KEY  (id),
 UNIQUE KEY rev (record_id,version)
 ) ENGINE=InnoDB $c;");
  dbDelta('CREATE TABLE '.self::table('requests')." (
 request_key varchar(64) NOT NULL,
 fingerprint varchar(64) NOT NULL,
 response longtext NOT NULL,
 PRIMARY KEY  (request_key)
 ) ENGINE=InnoDB $c;");
  dbDelta('CREATE TABLE '.self::table('assets')." (
 id varchar(36) NOT NULL,
 site_id varchar(36) NOT NULL,
 company_id varchar(36) NOT NULL DEFAULT '',
 author_id bigint NOT NULL,
 name varchar(200) NOT NULL,
 mime varchar(80) NOT NULL,
 digest varchar(64) NOT NULL,
 content longblob NOT NULL,
 created_at datetime NOT NULL,
 PRIMARY KEY  (id),
 KEY scope (site_id)
 ) ENGINE=InnoDB $c;");
  foreach(['hse_manager'=>'HSE referente','hse_company'=>'HSE impresa','hse_reader'=>'HSE lettore'] as $r=>$name) add_role($r,$name,['read'=>true]);
  update_option('hse_schema','1',false);
 }
 static function formats($row){return array_map(fn($k)=>in_array($k,['version','author_id'])?'%d':'%s',array_keys($row));}
 static function decode($r){if(!$r)throw new HSE_Fault('Record non trovato',404);$d=json_decode($r['payload'],true);return array_merge($d,['id'=>$r['id'],'kind'=>$r['kind'],'site_id'=>$r['site_id'],'company_id'=>$r['company_id'],'version'=>(int)$r['version'],'author_id'=>(int)$r['author_id'],'created_at'=>$r['created_at'].'Z','updated_at'=>$r['updated_at'].'Z']);}
 static function get($id){global $wpdb;return self::decode($wpdb->get_row($wpdb->prepare('SELECT * FROM '.self::table().' WHERE id=%s',$id),ARRAY_A));}
 static function list($kind,$site='') {global $wpdb;$q='SELECT * FROM '.self::table().' WHERE kind=%s';$a=[$kind];if($site!==''){$q.=' AND site_id=%s';$a[]=$site;}$rows=$wpdb->get_results($wpdb->prepare($q.' ORDER BY updated_at DESC,id',$a),ARRAY_A);return array_map([self::class,'decode'],$rows);}
 static function save($kind,$data,$id=null,$expected=0,$restore=false){
  global $wpdb;$now=gmdate('Y-m-d H:i:s');$old=$id&&!$restore?self::get($id):null;
  if($old && ($old['kind']!==$kind || $old['version']!==(int)$expected))throw new HSE_Fault('Conflitto: confronta la revisione corrente',409,$old);
  $id=$id?:wp_generate_uuid4();$v=$old?$old['version']+1:1;if($restore)$v=1+(int)$wpdb->get_var($wpdb->prepare('SELECT MAX(version) FROM '.self::table('revisions').' WHERE record_id=%s',$id));
  foreach(['id','kind','version','author_id','created_at','updated_at','expected_version','request_id'] as $k)unset($data[$k]);
  $row=['kind'=>$kind,'site_id'=>$data['site_id']??'','company_id'=>$data['company_id']??'','version'=>$v,'author_id'=>$old['author_id']??get_current_user_id(),'created_at'=>$old?substr($old['created_at'],0,19):$now,'updated_at'=>$now,'payload'=>wp_json_encode($data)];
  if($old){$ok=$wpdb->update(self::table(),$row,['id'=>$id,'version'=>$expected],self::formats($row),['%s','%d']);if($ok!==1)throw new HSE_Fault('Conflitto di revisione',409);}else{$row['id']=$id;if(!$wpdb->insert(self::table(),$row,self::formats($row)))throw new HSE_Fault('Archivio non disponibile',503);}
  if(!$wpdb->insert(self::table('revisions'),['record_id'=>$id,'version'=>$v,'payload'=>wp_json_encode($data),'created_at'=>$now,'author_id'=>get_current_user_id()]))throw new HSE_Fault('Revisione non salvata',503);
  return self::get($id);
 }
 static function atomic($request,$fingerprint,$callback){
  global $wpdb;if(!is_string($request)||!preg_match('/^[a-zA-Z0-9-]{16,100}$/',$request))throw new HSE_Fault('request_id obbligatorio');
  $key=hash('sha256',get_current_user_id().':'.$request);$fp=hash('sha256',$fingerprint);
  $wpdb->query('START TRANSACTION');
  try{
   $insert=$wpdb->query($wpdb->prepare('INSERT IGNORE INTO '.self::table('requests')." (request_key,fingerprint,response) VALUES (%s,%s,'')",$key,$fp));
   $row=$wpdb->get_row($wpdb->prepare('SELECT * FROM '.self::table('requests').' WHERE request_key=%s FOR UPDATE',$key),ARRAY_A);
   if(!$row)throw new HSE_Fault('Archivio richieste non disponibile',503);
   if($row['fingerprint']!==$fp)throw new HSE_Fault('request_id già usato con dati differenti',409);
   if(!$insert && $row['response']!==''){$wpdb->query('COMMIT');return json_decode($row['response'],true);}
   $result=$callback();$wpdb->update(self::table('requests'),['response'=>wp_json_encode($result)],['request_key'=>$key]);$wpdb->query('COMMIT');return $result;
  }catch(Throwable $e){$wpdb->query('ROLLBACK');throw $e;}
 }
 static function membership($site){foreach(self::list('memberships',$site) as $m)if((int)$m['user_id']===get_current_user_id())return $m;return null;}
 static function access($site,$write=false,$kind='',$record=null){
  if(current_user_can('manage_options'))return true;
  if(!$site)return false;$m=self::membership($site);if(!$m)return false;
  if($m['role']==='manager')return true;
  if($m['role']==='reader'&&$kind==='exports')return true;
  if($m['role']==='reader')return !$write && !in_array($kind,['memberships']);
  if($m['role']!=='company')return false;
  if(in_array($kind,['sites','areas','companies']))return !$write;
  if($record===null && !$write && in_array($kind,['plans','observations']))return true;
  if($kind==='plans' && !$write && !empty($m['share_plans']) && ($record['status']??'')==='Confirmed')return true;
  if(!in_array($kind,['plans','observations','assets','exports']))return false;
  return !empty($m['company_id']) && ($record['company_id']??'')===$m['company_id'];
 }
 static function permit($site,$write,$kind,$record=null){if(!self::access($site,$write,$kind,$record))throw new HSE_Fault('Accesso negato al cantiere o perimetro impresa',403);}
}
