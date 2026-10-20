<?php
require (getenv('HSE_QA_ROOT')?:'/var/www/hse-zip-030').'/wp-load.php';
if(PHP_VERSION!=='8.0.30'||HSE_VERSION!=='0.3.0')throw new RuntimeException('Unexpected installed runtime');
$file=getenv('HSE_QA_ZIP')?:'/tmp/hse-final-030.zip';$zip=new ZipArchive();if($zip->open($file)!==true)throw new RuntimeException('ZIP unavailable');$count=0;
for($i=0;$i<$zip->numFiles;$i++){$name=$zip->getNameIndex($i);if(!str_starts_with($name,'hse-risk-platform/')||str_contains($name,'..'))throw new RuntimeException('Unexpected ZIP entry');$target=WP_PLUGIN_DIR.'/'.$name;if(!is_file($target)||hash('sha256',$zip->getFromIndex($i))!==hash_file('sha256',$target))throw new RuntimeException('Installed file differs: '.$name);$count++;}
echo 'PASS final HTTP-installed ZIP: '.$count.' identical files, PHP '.PHP_VERSION.', SHA-256 '.hash_file('sha256',$file).PHP_EOL;
