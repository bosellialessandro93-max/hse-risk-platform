<?php
// Streamlit period adapter. Pure Risk Index calculations remain in the original engine.
class HSE_Period {
 static bool $restoring=false;
 static function weekly($d){return !empty($d['week']);}
 static function bounds($d){return self::weekly($d)?['from'=>$d['week'],'to'=>date('Y-m-d',strtotime($d['week'].' +6 days'))]:['from'=>$d['month'].'-01','to'=>date('Y-m-t',strtotime($d['month'].'-01'))];}
 static function validate(&$d,$old){
  if(self::weekly($d)){
   if(!HSE_Domain::date($d['week'])||date('N',strtotime($d['week']))!=='1'||$d['week']>HSE_Domain::today('Y-m-d'))throw new HSE_Fault('Scegli il lunedì di una settimana iniziata.',422,['field'=>'week']);
   if($old&&!self::weekly($old))throw new HSE_Fault('Le valutazioni mensili storiche mantengono il periodo originale. Crea una nuova valutazione settimanale.');
   $d['period_type']='week';$d['month']=substr($d['week'],0,7);$d['period_end']=self::bounds($d)['to'];
  }else{
   if(($old&&self::weekly($old))||(!$old&&!self::$restoring))throw new HSE_Fault('Indicare il lunedì della settimana.',422,['field'=>'week']);
   if(!preg_match('/^\d{4}-(0[1-9]|1[0-2])$/D',$d['month']??'')||$d['month']>HSE_Domain::today('Y-m'))throw new HSE_Fault('Mese storico non valido');
   $d['period_type']='month';
  }
  HSE_Domain::required($d,['phase','activities']);
 }
 static function event_in_period($e,$d){
  if(!self::weekly($d))return !empty($e['month'])&&$e['month']<=$d['month']&&($e['month']===$d['month']||$e['state']==='Open');
  $b=self::bounds($d);$date=$e['event_date']??'';
  // Undated legacy events cannot be assigned to a week by guessing.
  return HSE_Domain::date($date)&&$date<=$b['to']&&($date>=$b['from']||$e['state']==='Open');
 }
 static function session_in_period($session,$d){$b=self::bounds($d);return $session['held_on']>=$b['from']&&$session['held_on']<=$b['to'];}
 static function policy($weekly=true){$target=(int)get_option('hse_inspection_target',4);return ['version'=>'2.0.0-'.($weekly?'week-':'').'target-'.$target,'inspection_target'=>$target,'period_type'=>$weekly?'week':'month','source'=>'Target comune per periodo; nessuna conversione automatica del valore. Formule e coefficienti modello 2.0.0 invariati.'];}
 static function comparison($r,$site){
  HSE_Store::permit($site,false,'assessments');$week=$r->get_param('week');
  if(!HSE_Domain::date($week)||date('N',strtotime($week))!=='1'||date('Y-m-d',strtotime($week.' +6 days'))>=HSE_Domain::today('Y-m-d'))throw new HSE_Fault('Confronto: scegliere una settimana conclusa.');
  $items=[];$excluded=[];$policy=self::policy();
  foreach(HSE_Store::list('sites') as $s){if(!HSE_Store::access($s['id'],false,'assessments'))continue;$found=false;
   foreach(HSE_Risk::history($s['id']) as $a)if(($a['week']??'')===$week){if($a['model_version']===HSE_Risk::VERSION&&$a['policy']['version']===$policy['version']){$items[]=array_merge($a,['site_name'=>$s['name']]);$found=true;}}
   if(!$found)$excluded[]=['site'=>$s['name'],'reason'=>'Nessuna revisione settimanale salvata con modello e target comparabili'];
  }
  usort($items,fn($a,$b)=>$b['result']['base']<=>$a['result']['base']);return ['items'=>$items,'excluded'=>$excluded,'week'=>$week,'policy'=>$policy];
 }
 static function restore($kind,$d,$old){self::$restoring=true;try{return HSE_Domain::validate($kind,$d,$old);}finally{self::$restoring=false;}}
}
