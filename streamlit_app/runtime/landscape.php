<?php
// Only georeferenced raster images physically embedded in the uploaded KMZ. No network requests.
class HSE_Landscape {
 static function read($zip,$selected,&$warnings){
  $bytes=$zip->getFromName($selected);
  if(!is_string($bytes)||strlen($bytes)>15*1024*1024||preg_match('/<!DOCTYPE|<!ENTITY|<script|<iframe|<svg|javascript:|\son[a-z]+\s*=/i',$bytes))throw new HSE_Fault('KML non sicuro');
  $prev=libxml_use_internal_errors(true);$xml=simplexml_load_string($bytes,'SimpleXMLElement',LIBXML_NONET|LIBXML_NOBLANKS);libxml_clear_errors();libxml_use_internal_errors($prev);if(!$xml)throw new HSE_Fault('KML XML non valido');
  $out=[];$total=0;
  foreach($xml->xpath('//*[local-name()="GroundOverlay"]') as $overlay){
   $value=function($path)use($overlay){$v=$overlay->xpath($path);return trim((string)($v[0]??''));};
   $href=$value('./*[local-name()="Icon"]/*[local-name()="href"]');
   if(!$href||preg_match('~^[a-z]+:|^[/\\\\]|[?#\x00]~i',$href)){$warnings[]='Paesaggio remoto o percorso non sicuro: non caricato.';continue;}
   $parts=[];$safe=true;foreach(explode('/',str_replace('\\','/',dirname($selected).'/'.rawurldecode($href))) as $part){if($part===''||$part==='.')continue;if($part==='..'){if(!$parts){$safe=false;break;}array_pop($parts);}else $parts[]=$part;}
   if(!$safe){$warnings[]='Paesaggio con percorso fuori archivio: escluso.';continue;}
   $image=$zip->getFromName(implode('/',$parts));$size=is_string($image)?@getimagesizefromstring($image):false;
   if(!$size||!in_array($size['mime'],['image/png','image/jpeg'])||$size[0]*$size[1]>20000000){$warnings[]='Paesaggio assente, non PNG/JPEG o oltre 20 megapixel: escluso.';continue;}
   $bounds=[];foreach(['north','south','east','west','rotation'] as $key){$v=$value('./*[local-name()="LatLonBox"]/*[local-name()="'.$key.'"]');$bounds[$key]=$key==='rotation'&&$v===''?0:(is_numeric($v)?(float)$v:null);}
   if(!self::bounds($bounds)){$warnings[]='Paesaggio senza LatLonBox valido (quad/antimeridiano non supportati): escluso.';continue;}
   $total+=strlen($image);if($total>12*1024*1024||count($out)>=8)throw new HSE_Fault('Paesaggio: massimo 8 immagini, 12 MB complessivi.');
   $out[]=['name'=>sanitize_text_field($value('./*[local-name()="name"]')),'bounds'=>$bounds,'mime'=>$size['mime'],'chunks'=>str_split(base64_encode($image),524288)];
  }
  return $out;
 }
 static function bounds($b){foreach(['north','south','east','west','rotation'] as $k)if(!isset($b[$k])||!is_numeric($b[$k])||!is_finite((float)$b[$k]))return false;return $b['north']<90&&$b['south']> -90&&$b['north']>$b['south']&&$b['east']<=180&&$b['west']>= -180&&$b['east']>$b['west']&&abs($b['rotation'])<=360;}
 static function validate($layers){
  if(!is_array($layers)||count($layers)>8)throw new HSE_Fault('Paesaggio non valido');$total=0;
  foreach($layers as $layer){if(!is_array($layer)||!self::bounds($layer['bounds']??[])||!in_array($layer['mime']??'',['image/png','image/jpeg'])||!is_array($layer['chunks']??null)||count($layer['chunks'])>40)throw new HSE_Fault('Livello paesaggio non valido');
   foreach($layer['chunks'] as $chunk)if(!is_string($chunk)||strlen($chunk)>524288)throw new HSE_Fault('Immagine paesaggio non valida');
   $encoded=implode('',$layer['chunks']);if(strlen($encoded)>17*1024*1024)throw new HSE_Fault('Paesaggio oltre limite');$image=base64_decode($encoded,true);$size=$image!==false?@getimagesizefromstring($image):false;$total+=strlen($image?:'');if(!$size||$size['mime']!==$layer['mime']||$size[0]*$size[1]>20000000||$total>12*1024*1024)throw new HSE_Fault('Immagine paesaggio non valida o oltre limite');
  }
 }
}
