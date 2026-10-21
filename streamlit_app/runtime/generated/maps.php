<?php
if (!defined('ABSPATH')) exit;
class HSE_Maps {
 static function import($bytes,$name,$selected=''){
  if(strlen($bytes)>15*1024*1024)throw new HSE_Fault('Limite file: 15 MB');$warnings=[];$landscape=[];
  if(strtolower(pathinfo($name,PATHINFO_EXTENSION))==='kmz'){
   if(!class_exists('ZipArchive'))throw new HSE_Fault('Estensione PHP ZIP non disponibile',503);
   require_once ABSPATH.'wp-admin/includes/file.php';$tmp=wp_tempnam('hse-kmz');file_put_contents($tmp,$bytes);$z=new ZipArchive();
   try{
    if($z->open($tmp)!==true)throw new HSE_Fault('KMZ corrotto');if($z->numFiles>200)throw new HSE_Fault('KMZ: oltre 200 file');$total=0;$candidates=[];
    for($i=0;$i<$z->numFiles;$i++){$s=$z->statIndex($i);$path=str_replace('\\','/',$s['name']);if(str_starts_with($path,'/')||preg_match('~(^|/)\.\.(/|$)|^[A-Za-z]:|\x00~',$path))throw new HSE_Fault('KMZ: percorso non sicuro');$total+=$s['size'];if($total>50*1024*1024||$s['size']/max(1,$s['comp_size'])>200)throw new HSE_Fault('KMZ: decompressione eccessiva');$ext=strtolower(pathinfo($path,PATHINFO_EXTENSION));if(!in_array($ext,['kml','png','jpg','jpeg','gif','']))throw new HSE_Fault('KMZ: tipo file non consentito');if($ext==='kml')$candidates[]=$s['name'];}
    if(!$candidates)throw new HSE_Fault('KMZ senza KML');if(!$selected&&count($candidates)>1&& !in_array('doc.kml',$candidates))return ['candidates'=>$candidates,'selection_required'=>true];$selected=$selected?: (in_array('doc.kml',$candidates)?'doc.kml':$candidates[0]);if(!in_array($selected,$candidates))throw new HSE_Fault('KML selezionato inesistente');$landscape=HSE_Landscape::read($z,$selected,$warnings);$bytes=$z->getFromName($selected);$z->close();
   }finally{unlink($tmp);}
  }
  if(!function_exists('simplexml_load_string'))throw new HSE_Fault('Estensione XML non disponibile',503);
  if(strlen($bytes)>15*1024*1024||str_contains($bytes,"\0"))throw new HSE_Fault('KML oltre 15 MB o codifica non UTF-8');
  if(preg_match('/<!DOCTYPE|<!ENTITY|<script|<iframe|<svg|javascript:|\son[a-z]+\s*=/i',$bytes))throw new HSE_Fault('XML attivo o entità non consentite');
  $prev=libxml_use_internal_errors(true);$xml=simplexml_load_string($bytes,'SimpleXMLElement',LIBXML_NONET|LIBXML_NOBLANKS);libxml_clear_errors();libxml_use_internal_errors($prev);if(!$xml)throw new HSE_Fault('KML XML non valido');
  foreach(['NetworkLink','GroundOverlay','ScreenOverlay','Model','Tour'] as $type)if(!($type==='GroundOverlay'&&$landscape)&&$xml->xpath('//*[local-name()="'.$type.'"]'))$warnings[]=$type.': non importato; risorse remote non caricate';
  if($xml->xpath('//*[local-name()="Icon"]'))$warnings[]='Icone KML non importate: marker neutri; nessuna risorsa remota caricata';
  $styles=[];foreach($xml->xpath('//*[local-name()="Style"][@id]') as $st)$styles['#'.(string)$st['id']]=self::style($st);foreach($xml->xpath('//*[local-name()="StyleMap"][@id]') as $sm)foreach($sm->xpath('./*[local-name()="Pair"]') as $pair){$key=$pair->xpath('./*[local-name()="key"]');$url=$pair->xpath('./*[local-name()="styleUrl"]');if((string)($key[0]??'')==='normal')$styles['#'.(string)$sm['id']]=$styles[(string)($url[0]??'')]??[];}
  $features=[];foreach($xml->xpath('//*[local-name()="Placemark"]') as $p){$children=$p->xpath('./*');$g=null;$props=['name'=>'','category'=>'other','source_style'=>'','attributes'=>[],'folder'=>''];foreach($children as $c){$n=$c->getName();if($n==='name')$props['name']=sanitize_text_field((string)$c);elseif(in_array($n,['Point','LineString','Polygon','MultiGeometry']))$g=self::geometry($c);elseif($n==='styleUrl')$props['source_style']=sanitize_text_field((string)$c);elseif($n==='ExtendedData')foreach($c->xpath('.//*[local-name()="Data"]') as $a){$v=$a->xpath('./*[local-name()="value"]');$props['attributes'][sanitize_text_field((string)$a['name'])]=sanitize_text_field((string)($v[0]??''));}}
   $props['style']=$styles[$props['source_style']]??[];foreach($p->xpath('./*[local-name()="Style"]') as $st)$props['style']=array_merge($props['style'],self::style($st));if($p->xpath('.//*[local-name()="Icon"]')||$props['source_style']&&!str_starts_with($props['source_style'],'#'))$warnings[]='Icona/stile remoto non caricato: '.$props['name'];foreach($p->xpath('.//*[local-name()="SimpleData"]') as $a)$props['attributes'][sanitize_text_field((string)$a['name'])]=sanitize_text_field((string)$a);
   $folders=$p->xpath('ancestor::*[local-name()="Folder"]/*[local-name()="name"]');$props['folder']=implode(' / ',array_map('strval',$folders?:[]));
   if($g)$features[]=['type'=>'Feature','id'=>wp_generate_uuid4(),'properties'=>$props,'geometry'=>$g];else $warnings[]='Placemark non supportato: '.$props['name'];if(count($features)>10000)throw new HSE_Fault('Oltre 10000 feature');
  }
  if(!$features&&!$landscape)throw new HSE_Fault('Nessuna geometria compatibile');$geo=['type'=>'FeatureCollection','features'=>$features];self::validate($geo);return ['landscape'=>$landscape,'geojson'=>$geo,'warnings'=>$warnings,'source_sha256'=>hash('sha256',$bytes)];
 }
 static function style($s){$out=[];foreach(['LineStyle'=>['color'=>'stroke','width'=>'stroke_width'],'PolyStyle'=>['color'=>'fill','fill'=>'fill_enabled','outline'=>'outline_enabled'],'IconStyle'=>['scale'=>'point_scale'],'LabelStyle'=>['scale'=>'label_scale']] as $type=>$keys)foreach($keys as $tag=>$key){$v=$s->xpath('./*[local-name()="'.$type.'"]/*[local-name()="'.$tag.'"]');if(!$v)continue;$value=(string)$v[0];if($tag==='color'&&preg_match('/^[0-9a-f]{8}$/iD',$value)){$out[$key]='#'.substr($value,6,2).substr($value,4,2).substr($value,2,2).substr($value,0,2);}elseif(is_numeric($value))$out[$key]=max(0,min(20,(float)$value));}return $out;}
 static function coords($s){$r=[];if(substr_count($s,',')>100000)throw new HSE_Fault('Troppi vertici');foreach(preg_split('/\s+/',trim($s)) as $x){$v=explode(',',$x);if(count($v)<2||!is_numeric($v[0])||!is_numeric($v[1]))throw new HSE_Fault('Coordinate KML non valide');$pt=[(float)$v[0],(float)$v[1]];if(isset($v[2])&&is_numeric($v[2]))$pt[]=(float)$v[2];$r[]=$pt;}return $r;}
 static function geometry($e){$type=$e->getName();if($type==='MultiGeometry'){$gs=[];foreach($e->children() as $c){$g=self::geometry($c);if($g)$gs[]=$g;}return ['type'=>'GeometryCollection','geometries'=>$gs];}
  if($type==='Polygon'){$rings=[];foreach($e->xpath('.//*[local-name()="LinearRing"]/*[local-name()="coordinates"]') as $c)$rings[]=self::coords((string)$c);return ['type'=>'Polygon','coordinates'=>$rings];}
  if(in_array($type,['Point','LineString'])){$c=$e->xpath('./*[local-name()="coordinates"]');$pts=self::coords((string)($c[0]??''));return ['type'=>$type,'coordinates'=>$type==='Point'?($pts[0]??[]):$pts];}return null;
 }
 static function validate($geo){if(($geo['type']??'')!=='FeatureCollection'||!is_array($geo['features']??null)||count($geo['features'])>10000)throw new HSE_Fault('GeoJSON non valido');foreach($geo['features'] as $f){if(($f['type']??'')!=='Feature')throw new HSE_Fault('Feature non valida');self::check_geometry($f['geometry']??[],0);}}
 static function check_geometry($g,$depth){if($depth>8)throw new HSE_Fault('Geometria troppo annidata');if(($g['type']??'')==='GeometryCollection'){foreach($g['geometries']??[] as $child)self::check_geometry($child,$depth+1);return;}
  if(!in_array($g['type']??'',['Point','LineString','Polygon']))throw new HSE_Fault('Tipo geometria non supportato');$c=$g['coordinates']??[];$pts=$g['type']==='Point'?[$c]:($g['type']==='Polygon'?array_merge(...($c?:[[]])):$c);
  if(!$pts)throw new HSE_Fault('Coordinate mancanti');foreach($pts as $p)if(count($p)<2||!is_numeric($p[0])||!is_numeric($p[1])||abs($p[0])>180||abs($p[1])>90)throw new HSE_Fault('Coordinate fuori WGS84');
  if($g['type']==='LineString'&&count($pts)<2)throw new HSE_Fault('Linea incompleta');if($g['type']==='Polygon')foreach($c as $ring)if(count($ring)<4||$ring[0]!==$ring[count($ring)-1])throw new HSE_Fault('Anello poligono non chiuso');
 }
}
