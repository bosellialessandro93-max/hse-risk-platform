<?php
if (!defined('ABSPATH')) exit;
class HSE_API {
 static function routes(){
  register_rest_route('hse/v1','/(?P<path>.*)',['methods'=>'GET,POST,PATCH,DELETE','permission_callback'=>function(){return is_user_logged_in()?true:new WP_Error('hse_login','Autenticazione richiesta',['status'=>401]);},'callback'=>[self::class,'dispatch']]);
 }
 static function dispatch($r){try{$out=self::handle($r);$resp=new WP_REST_Response(['data'=>$out],200);$resp->header('Cache-Control','private, no-store');$resp->header('X-Robots-Tag','noindex');return $resp;}catch(HSE_Fault $e){return new WP_Error('hse_error',$e->getMessage(),['status'=>$e->status,'details'=>$e->details]);}catch(Throwable $e){error_log('HSE: '.$e->getMessage());return new WP_Error('hse_internal','Operazione non riuscita; dati non confermati',['status'=>500]);}}
 static function handle($r){
  if(strlen($r->get_body())>64*1024*1024)throw new HSE_Fault('Richiesta oltre 64 MB',413);$path=trim($r['path'],'/');$parts=explode('/',$path);$kind=$parts[0];$id=$parts[1]??null;$op=$parts[2]??null;$method=$r->get_method();$d=$r->get_json_params()?:[];$site=$r->get_param('site_id')?:($d['site_id']??'');
  if($kind==='capabilities'){$membership=$site?HSE_Store::membership($site):null;$writes=[];foreach(HSE_Domain::KINDS as $k)$writes[$k]=in_array($k,['sites','memberships','policies'])?current_user_can('manage_options'):HSE_Store::access($site,true,$k,['company_id'=>$membership['company_id']??'']);return ['membership'=>$membership,'can_write'=>$writes,'php'=>PHP_VERSION,'wordpress'=>get_bloginfo('version'),'zip'=>class_exists('ZipArchive'),'xml'=>function_exists('simplexml_load_string'),'images'=>extension_loaded('gd'),'upload_bytes'=>wp_max_upload_size(),'memory_limit'=>ini_get('memory_limit'),'execution_seconds'=>ini_get('max_execution_time'),'https'=>is_ssl(),'model_available'=>true,'model_version'=>HSE_Risk::VERSION,'methodology'=>HSE_Risk::policy(),'catalog'=>HSE_Risk::catalog()];}
  if($kind==='risk')return self::risk($r,$id,$d,$site);
  if($kind==='calendar'){HSE_Store::permit($site,false,'plans');return ['rows'=>HSE_Domain::calendar($site,$r->get_params()),'updated_at'=>gmdate('c'),'notice'=>'Programmazione dichiarata; nessuna autorizzazione al lavoro. Somma operatori per attività distinta dalla forza lavoro giornaliera.'];}
  if($kind==='exports'&&$id==='calendar'&&$method==='POST'){HSE_Store::permit($site,false,'plans');return HSE_Store::atomic($d['request_id']??'',wp_json_encode($d),function()use($site,$d){$m=HSE_Store::membership($site);$snapshot=['site_id'=>$site,'company_id'=>$m['company_id']??'','title'=>'Calendario esportato','rows'=>HSE_Domain::calendar($site,$d['filters']??[]),'filters'=>$d['filters']??[],'site_snapshot'=>HSE_Store::get($site),'generated_at'=>gmdate('c'),'exporter_version'=>HSE_VERSION];return HSE_Store::save('exports',$snapshot);});}
  if($kind==='assets')return self::assets($r,$id);
  if($kind==='maps'&&$id==='import'){HSE_Store::permit($site,true,'maps');$files=$r->get_file_params();$f=$files['file']??null;if(!$f||$f['error']!==UPLOAD_ERR_OK)throw new HSE_Fault('Upload non riuscito');return HSE_Maps::import(file_get_contents($f['tmp_name']),$f['name'],$r->get_param('selected')?:'');}
  if($kind==='backup'){HSE_Store::permit($site,true,'assessments');return self::backup($site,$r,$d);}
  if(!in_array($kind,HSE_Domain::KINDS))throw new HSE_Fault('Risorsa non trovata',404);
  if($method==='GET'){
   if($id){$record=HSE_Store::get($id);if($record['kind']!==$kind)throw new HSE_Fault('Risorsa non trovata',404);if(!($kind==='plans'&&$op==='revisions'&&HSE_Store::access($record['site_id'],false,'plans',null)))HSE_Store::permit($kind==='sites'?$id:$record['site_id'],false,$kind,$record);
    if($op==='revisions'){global $wpdb;$rows=$wpdb->get_results($wpdb->prepare('SELECT version,payload,created_at,author_id FROM '.HSE_Store::table('revisions').' WHERE record_id=%s ORDER BY version DESC',$id),ARRAY_A);foreach($rows as &$row)$row['payload']=json_decode($row['payload'],true);unset($row);return array_values(array_filter($rows,fn($rev)=>HSE_Store::access($record['site_id'],false,$kind,array_merge($record,$rev['payload']))));}return $record;}
   if($kind!=='sites')HSE_Store::permit($site,false,$kind);
   $rows=array_values(array_filter(HSE_Store::list($kind,$kind==='sites'?'':$site),fn($x)=>HSE_Store::access($kind==='sites'?$x['id']:$x['site_id'],false,$kind,$x)));
   $page=max(1,(int)($r->get_param('page')?:1));$size=min(500,max(1,(int)($r->get_param('per_page')?:100)));return ['items'=>array_slice($rows,($page-1)*$size,$size),'total'=>count($rows),'page'=>$page];
  }
  if($method==='DELETE'){if(!$id)throw new HSE_Fault('ID richiesto');$old=HSE_Store::get($id);if($old['kind']!==$kind)throw new HSE_Fault('Risorsa non trovata',404);HSE_Store::permit($old['site_id'],true,$kind,$old);if(!in_array($kind,['observations','assessments','plans'])||($old['status']??'')!=='Draft')throw new HSE_Fault('Solo bozze eliminabili; registrazioni e revisioni sono conservate',409);return HSE_Store::atomic($d['request_id']??'',wp_json_encode($d),function()use($kind,$old,$d){$old['status']='Discarded';return HSE_Store::save($kind,$old,$old['id'],$d['expected_version']??0);});}
  $old=null;$prepare=in_array($id,['prepare']);
  if($id&&!$prepare){$old=HSE_Store::get($id);if($old['kind']!==$kind)throw new HSE_Fault('Risorsa non trovata',404);$site=$old['site_id'];if($kind==='sites')$site=$id;
   if(isset($d['site_id'])&&$d['site_id']!==$old['site_id'])throw new HSE_Fault('Spostamento tra cantieri non consentito');
   if(isset($d['company_id'])&&$d['company_id']!==$old['company_id'])throw new HSE_Fault('Cambio impresa non consentito');
  }
  if(in_array($kind,['sites','memberships','policies'])&&!current_user_can('manage_options'))throw new HSE_Fault('Solo amministratore configurazione',403);
  $probe=$old?:$d;
  if($kind!=='sites')HSE_Store::permit($site,true,$kind,$probe);
  if($kind==='assessments'&&in_array($op,['calculate','save']))return self::risk($r,$op,array_merge($old,$d),$site);
  if($prepare){if($kind==='meetings')return HSE_Domain::prepare_meeting($site,$d);if($kind==='toolboxes')return HSE_Domain::toolbox($site,$d);throw new HSE_Fault('Preparazione non disponibile');}
  $request=$d['request_id']??'';$fingerprint=$method.':'.$path.':'.wp_json_encode($d);
  return HSE_Store::atomic($request,$fingerprint,function()use($kind,$d,$old,$id,$op,$site){
   $expected=$d['expected_version']??0;if($old&&$old['version']!==(int)$expected)throw new HSE_Fault('Conflitto di revisione',409,$old);
   if($op==='refresh'&&$kind==='meetings'){if($old['status']==='Finalized')throw new HSE_Fault('Verbale finalizzato: fonti immutabili',409);$proposal=HSE_Domain::prepare_meeting($site,['week'=>$old['week']??$old['meeting_date'],'observation_ids'=>$old['source_snapshot']['observation_ids']??[]]);if(empty($d['confirmed']))return ['previous'=>$old['source_snapshot'],'proposed'=>$proposal['source_snapshot'],'previous_items'=>count($old['items']),'proposed_items'=>count($proposal['items'])];$m=$old;$m['source_snapshot']=$proposal['source_snapshot'];$m['items']=$proposal['items'];return HSE_Store::save('meetings',$m,$id,$expected);}
   if($op==='formalize'&&$kind==='events'){$e=$old;$e['channel']='formal';$e['origin_id']=$old['origin_id']??$id;return HSE_Store::save('events',$e,$id,$expected);}
   if($op==='confirm'&&$kind==='plans'){$p=array_merge($old,$d);$p=HSE_Domain::confirm_plan($p);return HSE_Store::save($kind,$p,$id,$expected);}
   if($op==='finalize'&&$kind==='meetings'){
    if(($d['confirmed']??false)!==true)throw new HSE_Fault('Conferma contenuto richiesta');$m=$old;if($m['status']==='Finalized')return $m;
    foreach($m['items']??[] as $index=>&$item){if(!empty($item['action'])){HSE_Domain::required($item,['owner','due_date']);$action=['site_id'=>$site,'description'=>$item['action'],'owner'=>$item['owner'],'due_date'=>$item['due_date'],'status'=>'Open','source_type'=>'meetings','source_id'=>$id,'observation_id'=>$item['source_type']==='observations'?$item['source_id']:null];$action=HSE_Domain::validate('actions',$action);if(empty($item['action_id']))$item['action_id']=HSE_Store::save('actions',$action)['id'];else{$existing=HSE_Domain::reference($item['action_id'],'actions',$site);if(($existing['source_id']??'')!==$id)throw new HSE_Fault('Azione non collegata a questa riunione');if($existing['description']!==$action['description']||$existing['owner']!==$action['owner']||$existing['due_date']!==$action['due_date'])HSE_Store::save('actions',array_merge($existing,$action,['status'=>$existing['status']]),$existing['id'],$existing['version']);}}}unset($item);
    $m['status']='Finalized';$m['finalized_at']=gmdate('c');return HSE_Store::save('meetings',$m,$id,$expected);
   }
   if($op==='sessions'&&$kind==='toolboxes'){$s=$d;$s['site_id']=$site;$s['toolbox_id']=$id;$s=HSE_Domain::validate('sessions',$s);return HSE_Store::save('sessions',$s);}
   if($op)throw new HSE_Fault('Operazione non disponibile',404);if($kind==='exports'&&$old)throw new HSE_Fault('Snapshot export immutabile',409);
   $data=$old?array_merge($old,$d):$d;$data=HSE_Domain::validate($kind,$data,$old);return HSE_Store::save($kind,$data,$old?$id:null,$expected);
  });
 }
 static function risk($r,$op,$d,$site){
  if($op==='policy'){
   if(!current_user_can('manage_options'))throw new HSE_Fault('Solo amministratore configurazione',403);
   if($r->get_method()==='POST'){HSE_Domain::required($d,['inspection_target']);HSE_Domain::number($d,'inspection_target',1,1000,true);update_option('hse_inspection_target',(int)$d['inspection_target'],false);}return HSE_Risk::policy();
  }
  if($op==='history'){HSE_Store::permit($site,false,'assessments');return HSE_Risk::history($site);}
  if($op==='comparison'&&$r->get_param('week'))return HSE_Period::comparison($r,$site);
  if($op==='comparison'){
   HSE_Store::permit($site,false,'assessments');$month=$r->get_param('month');if(!preg_match('/^\d{4}-(0[1-9]|1[0-2])$/D',$month??'')||$month>=HSE_Domain::today('Y-m'))throw new HSE_Fault('Confronto: scegliere un mese concluso');$items=[];$excluded=[];$policy=HSE_Period::policy(false);
   foreach(HSE_Store::list('sites') as $s){if(!HSE_Store::access($s['id'],false,'assessments'))continue;$found=false;foreach(HSE_Risk::history($s['id']) as $a)if(empty($a['week'])&&$a['month']===$month){if($a['model_version']===HSE_Risk::VERSION&&$a['policy']['version']===$policy['version']){$items[]=array_merge($a,['site_name'=>$s['name']]);$found=true;}else $excluded[]=['site'=>$s['name'],'reason'=>'Versione modello o target differente'];}if(!$found)$excluded[]=['site'=>$s['name'],'reason'=>'Nessuna revisione salvata comparabile'];}
   usort($items,fn($a,$b)=>$b['result']['base']<=>$a['result']['base']);return ['items'=>$items,'excluded'=>$excluded,'month'=>$month,'policy'=>$policy];
  }
  if($r->get_method()!=='POST'||!in_array($op,['calculate','save','scenario','export']))throw new HSE_Fault('Operazione rischio non valida',404);
  $old=null;if(!empty($d['id'])){$old=HSE_Store::get($d['id']);if($old['kind']!=='assessments'||$old['site_id']!==$site)throw new HSE_Fault('Valutazione fuori cantiere',403);}
  HSE_Store::permit($site,true,'assessments',$old??$d);
  if(!in_array($op,['save','export']))return HSE_Risk::evaluate($d);
  if($op==='export'){if(!in_array($d['format']??'', ['pdf','docx','xlsx','pptx','management-pdf','json']))throw new HSE_Fault('Formato export non valido');return HSE_Store::atomic($d['request_id']??'',wp_json_encode($d),function()use($site,$d){$computed=self::validated_risk($d);$snapshot=['site_id'=>$site,'record'=>$computed,'site_snapshot'=>HSE_Store::get($site),'format'=>$d['format'],'generated_at'=>gmdate('c'),'model_version'=>HSE_Risk::VERSION,'input_hash'=>$computed['calculated_input_hash'],'history'=>HSE_Risk::history($site),'actions'=>array_values(array_filter(HSE_Store::list('actions',$site),fn($a)=>HSE_Store::access($site,false,'actions',$a))),'calendar'=>HSE_Domain::calendar($site,HSE_Period::bounds($computed))];$snapshot['snapshot_hash']=hash('sha256',wp_json_encode($snapshot));return HSE_Store::save('exports',$snapshot);});}
  return HSE_Store::atomic($d['request_id']??'',wp_json_encode($d),function()use($old,$d){$computed=self::validated_risk($d);$computed['status']='Saved';$computed['saved_at']=gmdate('c');return HSE_Store::save('assessments',$computed,$old['id']??null,$d['expected_version']??0);});
 }
 static function validated_risk($d){$computed=HSE_Risk::evaluate($d);if(empty($d['calculated_input_hash'])||!hash_equals($computed['calculated_input_hash'],$d['calculated_input_hash']))throw new HSE_Fault('Input o politica modificati: ricalcola prima di salvare',409);return $computed;}
 static function assets($r,$id){
  global $wpdb;$site=$r->get_param('site_id');
  if($r->get_method()==='GET'){$a=$wpdb->get_row($wpdb->prepare('SELECT * FROM '.HSE_Store::table('assets').' WHERE id=%s',$id),ARRAY_A);if(!$a)throw new HSE_Fault('Allegato non trovato',404);HSE_Store::permit($a['site_id'],false,'assets',$a);$a['base64']=base64_encode($a['content']);unset($a['content']);return $a;}
  $company=$r->get_param('company_id')?:'';HSE_Store::permit($site,true,'assets',['company_id'=>$company]);HSE_Domain::reference($site,'sites',$site);if($company)HSE_Domain::reference($company,'companies',$site);
  $files=$r->get_file_params();$f=$files['file']??null;if(!$f||$f['error']!==UPLOAD_ERR_OK||$f['size']>15*1024*1024)throw new HSE_Fault('Upload fallito o oltre 15 MB');$bytes=file_get_contents($f['tmp_name']);$mime=(new finfo(FILEINFO_MIME_TYPE))->buffer($bytes);if(!in_array($mime,['image/jpeg','image/png','application/pdf']))throw new HSE_Fault('Sono ammessi JPEG, PNG e PDF');
  if(str_starts_with($mime,'image/')){$size=getimagesizefromstring($bytes);if(!$size||$size[0]*$size[1]>20000000)throw new HSE_Fault('Immagine oltre 20 megapixel o non valida');}
  return HSE_Store::atomic($r->get_param('request_id'),$site.':'.$company.':'.hash('sha256',$bytes),function()use($wpdb,$site,$company,$f,$bytes,$mime){$id=wp_generate_uuid4();if(!$wpdb->insert(HSE_Store::table('assets'),['id'=>$id,'site_id'=>$site,'company_id'=>$company,'author_id'=>get_current_user_id(),'name'=>sanitize_file_name($f['name']),'mime'=>$mime,'digest'=>hash('sha256',$bytes),'content'=>$bytes,'created_at'=>gmdate('Y-m-d H:i:s')],['%s','%s','%s','%d','%s','%s','%s','%s','%s']))throw new HSE_Fault('Allegato non salvato',503);return ['id'=>$id,'name'=>sanitize_file_name($f['name']),'mime'=>$mime,'sha256'=>hash('sha256',$bytes)];});
 }
 static function backup($site,$r,$d){
  global $wpdb;$type=$r->get_param('type')?:($d['type']??'operations');
  $groups=['assessments'=>['areas','companies','toolboxes','sessions','events','assessments','policies'],'plans'=>['areas','companies','plans'],'operations'=>['areas','companies','observations','documents','maps','toolboxes','sessions','meetings','actions','checklists']];
  if(!isset($groups[$type]))throw new HSE_Fault('Tipo backup non valido');
  if($r->get_method()==='GET'){
   $records=[];$assetIds=[];foreach($groups[$type] as $k)foreach(HSE_Store::list($k,$site) as $x){$records[]=$x;foreach($x['attachments']??[] as $a)$assetIds[$a]=true;}
   $assets=[];foreach(array_keys($assetIds) as $id){$a=$wpdb->get_row($wpdb->prepare('SELECT * FROM '.HSE_Store::table('assets').' WHERE id=%s AND site_id=%s',$id,$site),ARRAY_A);if($a){$a['base64']=base64_encode($a['content']);unset($a['content']);$assets[]=$a;}}
   return ['schema_version'=>1,'type'=>$type,'site_id'=>$site,'generated_at'=>gmdate('c'),'records'=>$records,'assets'=>$assets,'notice'=>'Backup logico con allegati e riferimenti, cantiere originale richiesto. Per utenti, assegnazioni e tutte le revisioni usare anche backup completo database WordPress.'];
  }
  $b=$d['backup']??[];if(($b['schema_version']??0)!==1||($b['site_id']??'')!==$site||!is_array($b['records']??null)||count($b['records'])>10000)throw new HSE_Fault('Backup incompatibile o cantiere differente');$preview=[];
  foreach($b['records'] as $x){if(!in_array($x['kind']??'',$groups[$type])||($x['site_id']??'')!==$site||!wp_is_uuid($x['id']??''))throw new HSE_Fault('Record fuori perimetro');$preview[]=['id'=>$x['id'],'kind'=>$x['kind'],'version'=>$x['version']];}
  foreach($b['assets']??[] as $a){$bytes=base64_decode($a['base64']??'',true);if(($a['site_id']??'')!==$site||!wp_is_uuid($a['id']??'')||$bytes===false||strlen($bytes)>15*1024*1024||hash('sha256',$bytes)!==($a['digest']??'')||!in_array((new finfo(FILEINFO_MIME_TYPE))->buffer($bytes),['image/jpeg','image/png','application/pdf']))throw new HSE_Fault('Allegato backup non valido');}
  if(empty($d['confirm']))return ['preview'=>$preview,'notice'=>'Ripristino atomico con nuove revisioni e allegati verificati; eseguire prima backup database.'];
  return HSE_Store::atomic($d['request_id']??'',wp_json_encode($d),function()use($b,$site,$groups,$type,$wpdb){
   foreach($b['assets']??[] as $a){$existing=$wpdb->get_row($wpdb->prepare('SELECT site_id,digest FROM '.HSE_Store::table('assets').' WHERE id=%s',$a['id']),ARRAY_A);if($existing){if($existing['site_id']!==$site||$existing['digest']!==$a['digest'])throw new HSE_Fault('Conflitto allegato backup',409);continue;}
    $row=['id'=>$a['id'],'site_id'=>$site,'company_id'=>$a['company_id']??'','author_id'=>get_current_user_id(),'name'=>sanitize_file_name($a['name']),'mime'=>(new finfo(FILEINFO_MIME_TYPE))->buffer(base64_decode($a['base64'])),'digest'=>$a['digest'],'content'=>base64_decode($a['base64']),'created_at'=>gmdate('Y-m-d H:i:s')];
    if(!$wpdb->insert(HSE_Store::table('assets'),$row,['%s','%s','%s','%d','%s','%s','%s','%s','%s']))throw new HSE_Fault('Ripristino allegato non riuscito',503);
   }
   $out=[];$pending=$b['records'];$lastError=null;
   // Resolve cross-module links in dependency order; defer unresolved records and roll back if no progress.
   while($pending){$next=[];$progress=false;foreach($pending as $x){try{$old=null;try{$old=HSE_Store::get($x['id']);}catch(HSE_Fault $e){if($e->status!==404)throw $e;}
     if($old&&($old['site_id']!==$site||$old['kind']!==$x['kind']))throw new HSE_Fault('Conflitto identità backup',409);
     if($x['kind']==='meetings')$x['revision_reason']='Ripristino esplicito da backup';$data=HSE_Period::restore($x['kind'],$x,$old);
     // Restored publications must be reviewed before publishing; finalized meetings keep their immutable snapshot.
     if($x['kind']==='meetings'&&($x['status']??'')==='Finalized'){$data['status']='Finalized';$data['source_snapshot']=$x['source_snapshot']??[];}
     $saved=HSE_Store::save($x['kind'],$data,$x['id'],$old?$old['version']:0,!$old);$out[]=['id'=>$saved['id'],'version'=>$saved['version'],'status'=>'restored'];$progress=true;
    }catch(HSE_Fault $e){$next[]=$x;$lastError=$e;}}
    if(!$progress&&$next)throw new HSE_Fault('Ripristino annullato: '.$lastError->getMessage(),422,['records'=>array_column($next,'id')]);$pending=$next;
   }
   return $out;
  });
 }
}
