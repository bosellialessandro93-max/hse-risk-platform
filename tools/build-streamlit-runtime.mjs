import fs from 'node:fs';
// Checked replacements isolate Streamlit period/import behavior from the WordPress distribution.
const source='hse-risk-platform/includes/',dest='streamlit_app/runtime/generated/';fs.mkdirSync(dest,{recursive:true});
for(const name of ['domain','risk','maps','api']){
 let code=fs.readFileSync(source+name+'.php','utf8');
 const replace=(before,after)=>{if(!code.includes(before))throw Error('Runtime boundary changed: '+name+': '+before.slice(0,90));code=code.replace(before,after);};
 if(name==='domain'){
  replace("__DIR__.'/toolbox-catalog.json'","dirname(__DIR__,3).'/hse-risk-platform/includes/toolbox-catalog.json'");
  replace("self::required($d,['month','phase','activities']);if(!preg_match('/^\\d{4}-(0[1-9]|1[0-2])$/D',$d['month'])||$d['month']>self::today('Y-m'))throw new HSE_Fault('Mese futuro o non valido');","HSE_Period::validate($d,$old);");
  replace("(int)date('t',strtotime($d['month'].'-01'))", "(HSE_Period::weekly($d)?7:(int)date('t',strtotime($d['month'].'-01')))");
  replace("empty($e['month'])||$e['month']>$d['month']||($e['month']<$d['month']&&$e['state']!=='Open')", "!HSE_Period::event_in_period($e,$d)");
  replace("substr($session['held_on'],0,7)!==$d['month']", "!HSE_Period::session_in_period($session,$d)");
  replace("Incontro fuori mese", "Incontro fuori periodo");
  replace("case 'events':", "case 'events':if(!empty($d['event_date'])){if(!self::date($d['event_date'])||$d['event_date']>self::today('Y-m-d'))throw new HSE_Fault('Data segnalazione non valida');$d['month']=substr($d['event_date'],0,7);}");
  replace("HSE_Maps::validate($d['geojson']);", "HSE_Maps::validate($d['geojson']);HSE_Landscape::validate($d['landscape']??[]);if(!in_array($d['map_layout']??'light',['light','landscape']))throw new HSE_Fault('Layout mappa non valido');");
  replace("['from'=>$source['month'].'-01','to'=>date('Y-m-t',strtotime($source['month'].'-01'))]", "HSE_Period::bounds($source)");
 }
 if(name==='risk'){
  replace("__DIR__.'/risk-catalog.json'", "dirname(__DIR__,3).'/hse-risk-platform/includes/risk-catalog.json'");
  const policyStart=code.indexOf(' static function policy()'),policyEnd=code.indexOf(' static function level(',policyStart);
  code=code.slice(0,policyStart)+" static function policy(){return HSE_Period::policy();}\n"+code.slice(policyEnd);
  replace("'inspection_target'=>self::policy()['inspection_target']", "'inspection_target'=>HSE_Period::policy(HSE_Period::weekly($record))['inspection_target']");
  replace("$policy=self::policy();$record['policy']", "$policy=HSE_Period::policy(HSE_Period::weekly($record));$record['policy']");
  replace("['site_id','month','phase'", "['site_id','month','week','period_type','period_end','phase'");
  replace("$site.'/'.$p['month'].'/'.$p['model_version']", "$site.'/'.(!empty($p['week'])?'week/'.$p['week']:'month/'.$p['month']).'/'.$p['model_version']");
  replace("strcmp($a['month'],$b['month'])", "strcmp($a['week']??$a['month'],$b['week']??$b['month'])");
 }
 if(name==='api'){
  replace("if($op==='comparison'){", "if($op==='comparison'&&$r->get_param('week'))return HSE_Period::comparison($r,$site);\n  if($op==='comparison'){");
  replace("if($a['month']===$month)", "if(empty($a['week'])&&$a['month']===$month)");
  // Legacy comparison still uses the original monthly policy version.
  replace("$items=[];$excluded=[];$policy=HSE_Risk::policy();", "$items=[];$excluded=[];$policy=HSE_Period::policy(false);");
  replace("['from'=>$computed['month'].'-01','to'=>date('Y-m-t',strtotime($computed['month'].'-01'))]", "HSE_Period::bounds($computed)");
  replace("$data=HSE_Domain::validate($x['kind'],$x,$old);", "$data=HSE_Period::restore($x['kind'],$x,$old);");
 }
 if(name==='maps'){
  replace("$warnings=[];", "$warnings=[];$landscape=[];");
  replace("$bytes=$z->getFromName($selected);", "$landscape=HSE_Landscape::read($z,$selected,$warnings);$bytes=$z->getFromName($selected);");
  replace("if($xml->xpath('//*[local-name()=\"'.$type.'\"]'))", "if(!($type==='GroundOverlay'&&$landscape)&&$xml->xpath('//*[local-name()=\"'.$type.'\"]'))");
  replace("if(!$features)throw", "if(!$features&&!$landscape)throw");
  replace("return ['geojson'=>$geo,", "return ['landscape'=>$landscape,'geojson'=>$geo,");
 }
 const original=fs.readFileSync(source+name+'.php','utf8');
 if(name==='risk'){
  // Protect the complete pure calculation/scenario region byte-for-byte.
  const pure=s=>s.slice(s.indexOf(' static function level('),s.indexOf(' static function input('));
  if(pure(code)!==pure(original))throw Error('Pure Risk Index engine changed');
 }
 fs.writeFileSync(dest+name+'.php',code);
}
