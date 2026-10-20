<?php
require dirname(__DIR__,2).'/streamlit_app/runtime/compatibility.php';define('ABSPATH',dirname(__DIR__,2).'/streamlit_app/runtime/');require dirname(__DIR__,2).'/hse-risk-platform/includes/store.php';require dirname(__DIR__,2).'/hse-risk-platform/includes/risk.php';
$values=[0,20,20.00001,40,40.00001,60,60.00001,80,80.00001,100];$expected=['Basso','Basso','Medio basso','Medio basso','Medio','Medio','Alto','Alto','Critico','Critico'];foreach($values as $i=>$value)if(HSE_Risk::level($value)!==$expected[$i])throw new RuntimeException('Classification boundary changed');
$files=array_merge(glob(dirname(__DIR__,2).'/streamlit_app/runtime/*.php'),glob(dirname(__DIR__,2).'/hse-risk-platform/includes/*.php'));foreach($files as $file)token_get_all(file_get_contents($file),TOKEN_PARSE);
foreach(['mysqli','mbstring','fileinfo','simplexml','zip'] as $ext)if(!extension_loaded($ext))throw new RuntimeException('Missing '.$ext);
echo 'PASS PHP '.PHP_VERSION.': '.count($files).' domain/adapter files parsed, extensions and 10 exact/adjacent thresholds'.PHP_EOL;
