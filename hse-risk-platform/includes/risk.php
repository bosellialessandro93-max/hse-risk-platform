<?php
if (!defined('ABSPATH')) exit;
/** Direct port of the supplied document's pure MODEL_VERSION=2.0.0 functions.
 * No Streamlit/pandas/AI dependency. See docs/MODEL_2_0_0.md and parity tests. */
class HSE_Risk {
 const VERSION='2.0.0';
 static function catalog(){static $c;if($c===null){$raw=@file_get_contents(__DIR__.'/risk-catalog.json');$c=$raw!==false?json_decode($raw,true):null;if(!is_array($c)||!isset($c['PHASE_THEMES'],$c['WEIGHTS']))throw new HSE_Fault('Catalogo modello non leggibile o non valido: reinstallare il pacchetto',503);}return $c;}
 static function policy(){ $target=(int)get_option('hse_inspection_target',4);return ['version'=>'2.0.0-target-'.$target,'inspection_target'=>$target,'source'=>'Politica comune amministratore; valore iniziale 4 dal default_data originale']; }
 static function level($x){return ['Basso','Medio basso','Medio','Alto','Critico'][min(4,max(0,(int)ceil($x/20)-1))];}
 static function rounded($x,$digits){return (float)sprintf('%.' . $digits . 'f',$x);}
 static function bounded($x){return max(0,min(100,$x));}
 static function load($rows){$c=self::catalog();$sum=0.;foreach($rows as $r)$sum+=$c['SEVERITY'][$r['severity']]*$c['THEME_FACTOR'][$r['theme']]*$c['STATUS'][$r['status']]*($r['late']?1.25:1)*($r['repeat']?1.2:1);return $sum;}
 static function needs($d){$c=self::catalog();$needs=[];$reasons=[];
  foreach($d['activities'] as $a){$t=$c['ACTIVITY_THEME'][$a];$needs[$t]=max($needs[$t]??0,$c['ACTIVITY'][$a]/100);$reasons[$t][]='attività: '.$a;}
  foreach(['nc_items'=>['NC formale',1.],'crit_items'=>['criticità informale',.5]] as $key=>[$label,$factor])foreach($d[$key] as $r)if($r['status']==='Aperta'){$t=$r['theme'];$needs[$t]=($needs[$t]??0)+$c['SEVERITY'][$r['severity']]/5*$factor;$reasons[$t][]=$label.' aperta, gravità '.$r['severity'];}
  foreach($c['PHASE_THEMES'][$d['fase']] as $t){$needs[$t]=max($needs[$t]??0,.2);$reasons[$t][]='coerenza con fase '.$d['fase'];}return [$needs,$reasons];
 }
 static function calculate($d){
  $c=self::catalog();$ncLoad=self::load($d['nc_items']);$critLoad=self::load($d['crit_items']);
  $nc=100*(1-exp(-$ncLoad/10));$crit=100*(1-exp(-$critLoad/12));
  $activity=min(100,max(array_map(fn($a)=>$c['ACTIVITY'][$a],$d['activities']))+3*(count($d['activities'])-1));
  $interference=($d['interference_level']-1)/9*100;
  $org=100*(1-exp(-(max(0,$d['app']-1)+1.2*$d['sub'])/8));
  $deficit=100*(1-min(1,$d['inspections']/$d['inspection_target']));
  $controls=.65*(100-$d['hse_coverage'])+.35*$deficit;
  $components=array_combine(array_keys($c['WEIGHTS']),[$nc,$crit,$activity,$interference,$org,$controls]);$drivers=[];
  foreach($components as $key=>$value)$drivers[]=['Area'=>$key,'Indice area'=>self::rounded($value,3),'Peso massimo'=>$c['WEIGHTS'][$key],'Contributo'=>$value*$c['WEIGHTS'][$key]/100];
  $positive=min(2.,$d['stop_positive']*.5);$negative=min(6.,$d['stop_negative']*1.5);
  [$needs,$reasons]=self::needs($d);$numerator=0.;$details=[];
  foreach($d['awareness'] as $row){$t=$row['theme'];$coverage=$row['coverage']!==null?$row['coverage']/100:.5;$continuity=min(1.,.7+.1*($row['count']-1));$effectiveness=$coverage*$continuity;$numerator+=($needs[$t]??0)*$effectiveness;
   $details[]=['Tema'=>$t,'Incontri'=>$row['count'],'Copertura'=>$row['coverage']!==null?sprintf('%.0f%%',$row['coverage']):'Non nota: fattore 50%','Pertinenza'=>self::rounded($needs[$t]??0,3),'Efficacia convenzionale'=>self::rounded($effectiveness,3),'Motivo'=>implode('; ',$reasons[$t]??['Nessun collegamento agli input: nessun bonus'])];}
  $awareness=$needs?8*$numerator/array_sum($needs):0.;
  $raw=array_sum(array_column($drivers,'Contributo'))+$negative-$positive-$awareness;
  $high=count(array_filter($d['nc_items'],fn($r)=>$r['severity']==='alta'&&$r['status']==='Aperta'));
  $floor=$d['imminent_danger']||$high>=2?81.:($high===1?61.:0.);
  $reason=$d['imminent_danger']?'Pericolo grave e attuale dichiarato':($high>=2?'Almeno due NC formali alte aperte':($high?'Una NC formale alta aperta':'Nessuna soglia minima attiva'));
  $score=max($floor,self::bounded($raw));$target=null;$basis='Nessun dato di esposizione disponibile';$context=null;
  if(!empty($d['hours'])){$target=max(1.,$d['hours']/2000);$basis='1 ispezione ogni 2.000 ore lavorate';}
  elseif(!empty($d['days'])){$target=max(1.,$d['days']/5*max(1.,($d['workers']?:50)/50));$basis='1 ispezione ogni 5 giorni operativi e ogni 50 lavoratori medi (minimo fattore 1)';}
  elseif(!empty($d['workers'])){$target=max(1.,4*$d['workers']/50);$basis='4 ispezioni per 50 lavoratori medi nel mese';}
  if($target){$contextControls=.65*(100-$d['hse_coverage'])+.35*100*(1-min(1.,$d['inspections']/$target));$context=max($floor,self::bounded($raw+($contextControls-$controls)*.15));}
  foreach([['Stop Work negativi',6,$negative],['Stop Work positivi',-2,-$positive],['Sensibilizzazioni pertinenti',-8,-$awareness],['Limite scala 0–100',null,self::bounded($raw)-$raw],['Soglia minima di tutela',null,$score-self::bounded($raw)]] as [$label,$weight,$value])$drivers[]=['Area'=>$label,'Indice area'=>null,'Peso massimo'=>$weight,'Contributo'=>$value];
  $missing=[];if(!$d['inspections'])$missing[]='Nessuna ispezione: assenza di NC non dimostra assenza di anomalie.';
  if(in_array(null,[$d['hours'],$d['workers'],$d['days']],true))$missing[]='Dati di esposizione parziali o assenti: usare l’indice base per la graduatoria comune.';
  foreach($d['awareness'] as $row)if($row['coverage']===null){$missing[]='Copertura delle sensibilizzazioni non sempre nota.';break;}
  return ['version'=>self::VERSION,'score'=>self::rounded($score,2),'base'=>$score,'level'=>self::level($score),'raw'=>self::rounded($raw,3),'raw_exact'=>$raw,'floor'=>$floor,'floor_reason'=>$reason,'drivers'=>$drivers,'awareness_details'=>$details,'awareness_bonus'=>self::rounded($awareness,3),'needs'=>$needs,'reasons'=>$reasons,'context_score'=>$context!==null?self::rounded($context,2):null,'context_exact'=>$context,'context_target'=>$target?self::rounded($target,2):null,'context_basis'=>$basis,'missing'=>$missing,'detection'=>['formal_nc'=>count($d['nc_items']),'inspections'=>$d['inspections'],'ratio'=>$d['inspections']?count($d['nc_items'])/$d['inspections']:null,'effect'=>'Descrittivo; nessun malus NC/ispezioni','inspection_deficit'=>$deficit], 'explanations'=>self::method($d)];
 }
 static function method($d){return [
 'Carico = gravità (1/2,5/5) × tema (catalogo 0,65–1,25) × stato (aperta 1; chiusa nei tempi 0,2; in ritardo 0,4) × scaduta 1,25 × ricorrente 1,2.',
 'NC: 100 × (1 − exp(−carico/10)) × 0,30. Informali: 100 × (1 − exp(−carico/12)) × 0,08.',
 'Attività: min(100, massimo catalogo + 3 × (numero tipologie − 1)) × 0,22.',
 'Interferenze: (livello − 1)/9 × 100 × 0,15.',
 'Organizzazione: 100 × (1 − exp(−(max(0,appaltatrici−1) + 1,2 × subappaltatrici)/8)) × 0,10.',
 'Presidio: (0,65 × deficit copertura + 0,35 × deficit ispezioni) × 0,15. Deficit ispezioni = 100 × (1 − min(1,ispezioni/target)). Target comune: '.$d['inspection_target'].'. Nessun malus NC/ispezioni; zero ispezioni dà deficit 100.',
 'Stop Work: negativi +min(6,1,5 × numero); positivi −min(2,0,5 × numero).',
 'Bonus temi pertinenti = 8 × somma(necessità tema × copertura × min(1,0,7+0,1×(incontri−1)))/somma(necessità). Copertura ignota 0,5; cataloghi e ragioni nel dettaglio.',
 'Limite 0–100, poi soglia 61 per una NC formale alta aperta; 81 per almeno due o pericolo attuale. Fascia sul valore non arrotondato.',
 'Contesto: cambia solo deficit ispettivo. Ore/2000, altrimenti giorni/5 × max(1,lavoratori/50; assenti=50), altrimenti 4×lavoratori/50; target minimo 1.',
 'Modello gestionale sperimentale 2.0.0, non probabilità di infortunio. Coefficienti dalla fonte fornita; nessuna calibrazione inventata.'
 ];}
 static function scenarios($d,$baseline){$changes=[
 'Chiusura verificata delle NC aperte'=>function(&$x){foreach($x['nc_items'] as &$r)if($r['status']==='Aperta'){$r['status']='Chiusa nei tempi';$r['late']=false;}},
 'Chiusura verificata delle criticità aperte'=>function(&$x){foreach($x['crit_items'] as &$r)if($r['status']==='Aperta'){$r['status']='Chiusa nei tempi';$r['late']=false;}},
 'Copertura HSE al 100%'=>function(&$x){$x['hse_coverage']=100;},
 'Target ispettivo raggiunto'=>function(&$x){$x['inspections']=max($x['inspections'],$x['inspection_target']);},
 'Interferenza ridotta di 2 livelli'=>function(&$x){$x['interference_level']=max(1,$x['interference_level']-2);},
 'Toolbox pertinenti: 4 incontri per tema, copertura 100%'=>function(&$x){[$needs]=self::needs($x);$x['awareness']=array_map(fn($t)=>['theme'=>$t,'count'=>4,'coverage'=>100.],array_keys($needs));}];$rows=[];
 foreach($changes as $label=>$change){$sample=$d;$change($sample);$r=self::calculate($sample);$rows[]=['Scenario indipendente'=>$label,'Indice simulato'=>$r['score'],'Riduzione punti'=>self::rounded($baseline['score']-$r['score'],2),'Soglia residua'=>$r['floor']];}return $rows;}
 static function input($record){$c=self::catalog();$map=['app'=>'contractors','sub'=>'subcontractors','company_hse'=>'hse_professionals','hse_coverage'=>'coverage','interference_level'=>'interference','inspections'=>'inspections','stop_positive'=>'stop_positive','stop_negative'=>'stop_negative'];$d=['activities'=>$record['activities'],'fase'=>mb_strtolower(trim($record['phase'])),'nc_items'=>[],'crit_items'=>[],'awareness'=>[],'imminent_danger'=>($record['grave_danger']??false)===true,'inspection_target'=>self::policy()['inspection_target']];
  // Only documented historical display aliases, never fuzzy matching.
  $aliases=['scavo'=>'scavi','scavi'=>'scavi','civili'=>'civili'];$d['activities']=array_map(fn($a)=>$aliases[mb_strtolower(trim($a))]??mb_strtolower(trim($a)),$d['activities']);
  if(!isset($c['PHASE_THEMES'][$d['fase']]))throw new HSE_Fault('Fase fuori catalogo modello 2.0.0',422,['field'=>'phase']);
  if(count($d['activities'])!==count(array_unique($d['activities']))||array_diff($d['activities'],array_keys($c['ACTIVITY'])))throw new HSE_Fault('Lavorazioni fuori catalogo o duplicate',422,['field'=>'activities']);
  foreach($map as $dest=>$key){$v=$record[$key]??null;if(in_array($dest,['app','hse_coverage','interference_level'])&&$v===null)throw new HSE_Fault('Dato necessario al calcolo: '.$key,422,['field'=>$key]);$d[$dest]=$v??0;}
  foreach(['app'=>[0,200],'sub'=>[0,200],'company_hse'=>[0,200],'hse_coverage'=>[0,100],'inspections'=>[0,2000],'interference_level'=>[1,10],'stop_positive'=>[0,1000],'stop_negative'=>[0,1000]] as $k=>[$lo,$hi]){if(!is_numeric($d[$k])||is_bool($d[$k])||!is_finite((float)$d[$k])||$d[$k]<$lo||$d[$k]>$hi||($k!=='hse_coverage'&&(int)$d[$k]!=(float)$d[$k]))throw new HSE_Fault('Valore fuori contratto modello: '.$k,422,['field'=>$map[$k]??$k]);}
  if(isset($record['grave_danger'])&&!is_bool($record['grave_danger']))throw new HSE_Fault('Pericolo attuale: usare sì/no',422,['field'=>'grave_danger']);
  foreach(['hours'=>10000000,'workers'=>100000,'days'=>31] as $k=>$hi)HSE_Domain::number($record,$k,0,$hi,false);
  if(count($record['events']??[]) + count($record['event_snapshots']??[])>2000||count($record['sensitizations']??[])>500)throw new HSE_Fault('Troppi eventi o sensibilizzazioni');
  foreach(['hours','workers','days'] as $key)$d[$key]=empty($record[$key])?null:$record[$key];
  foreach(array_merge($record['events']??[],$record['event_snapshots']??[]) as $e){$theme=mb_strtolower(trim($e['topic']));if(!in_array($theme,$c['THEMES']))throw new HSE_Fault('Tema evento fuori catalogo: '.$e['topic'],422,['field'=>'topic']);$d[$e['channel']==='formal'?'nc_items':'crit_items'][]=['theme'=>$theme,'severity'=>['Low'=>'bassa','Medium'=>'media','High'=>'alta'][$e['severity']],'status'=>['Open'=>'Aperta','Closed on time'=>'Chiusa nei tempi','Closed late'=>'Chiusa in ritardo'][$e['state']],'late'=>!empty($e['overdue']),'repeat'=>!empty($e['recurring'])];}
  if(count($d['nc_items'])>1000||count($d['crit_items'])>1000)throw new HSE_Fault('Massimo 1000 eventi per canale');
  $topics=[];foreach($record['sensitizations']??[] as $s){$t=mb_strtolower(trim($s['topic']));if(!in_array($t,$c['THEMES'])||in_array($t,$topics))throw new HSE_Fault('Tema sensibilizzazione fuori catalogo o duplicato',422,['field'=>'topic']);$topics[]=$t;HSE_Domain::number($s,'count',1,1000,true);$d['awareness'][]=['theme'=>$t,'count'=>$s['count'],'coverage'=>$s['coverage']??null];}return $d;
 }
 static function evaluate($record){$old=!empty($record['id'])?HSE_Store::get($record['id']):null;$record=HSE_Domain::validate('assessments',$record,$old);$input=self::input($record);$policy=self::policy();$record['policy']=$policy;$record['model_version']=self::VERSION;$record['model_input']=$input;$semantic=[];foreach(['site_id','month','phase','activities','contractors','subcontractors','hse_professionals','coverage','interference','inspections','stop_positive','stop_negative','grave_danger','hours','workers','days','events','event_snapshots','sensitizations','notes'] as $k)$semantic[$k]=$record[$k]??null;$record['calculated_input_hash']=hash('sha256',wp_json_encode([$input,$policy,$semantic]));$record['result']=self::calculate($input);$record['result']['policy']=$policy;$record['scenarios']=self::scenarios($input,$record['result']);$record['status']='Calculated';$record['calculated_at']=gmdate('c');return $record;}
 static function history($site){global $wpdb;$all=[];foreach(HSE_Store::list('assessments',$site) as $r){$revs=$wpdb->get_results($wpdb->prepare('SELECT id,version,payload,created_at FROM '.HSE_Store::table('revisions').' WHERE record_id=%s ORDER BY version DESC',$r['id']),ARRAY_A);foreach($revs as $v){$p=json_decode($v['payload'],true);if(($p['status']??'')!=='Saved')continue;$key=$site.'/'.$p['month'].'/'.$p['model_version'];$entry=array_merge($r,$p,['version'=>(int)$v['version'],'updated_at'=>$v['created_at'],'saved_revision_id'=>(int)$v['id']]);if(!isset($all[$key])||$entry['saved_revision_id']>$all[$key]['saved_revision_id'])$all[$key]=$entry;break;}}usort($all,fn($a,$b)=>strcmp($a['month'],$b['month']));return array_values($all);}
}
