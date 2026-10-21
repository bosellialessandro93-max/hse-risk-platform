<?php
// CLI only: never exposed as an HTTP service. Actor and DB configuration come from Python.
if(PHP_SAPI!=='cli')exit(1);
error_reporting(E_ALL);ini_set('display_errors','0');date_default_timezone_set('UTC');
require __DIR__.'/compatibility.php';require __DIR__.'/postgres.php';define('ABSPATH',__DIR__.'/');define('HSE_VERSION','0.3.0-streamlit');
$source=dirname(__DIR__,2).'/hse-risk-platform/includes/';foreach(['store','domain','risk','maps','api'] as $name)require $source.$name.'.php';
$tmp=[];
try{
 $input=json_decode(stream_get_contents(STDIN),true,512,JSON_THROW_ON_ERROR);$GLOBALS['hse_actor']=$input['actor']??['id'=>0,'is_admin'=>false];
 if(!is_user_logged_in())throw new HSE_Fault('Autenticazione richiesta',401);
 if(($input['action']??'')==='calculate_model'){$models=$input['model'];$calculate=function($model){$value=HSE_Risk::calculate($model);$value['scenarios']=HSE_Risk::scenarios($model,$value);return $value;};echo wp_json_encode(['data'=>isset($models[0])?array_map($calculate,$models):$calculate($models)]);exit;}
 $config=json_decode(getenv('HSE_DATABASE'),true,512,JSON_THROW_ON_ERROR);$wpdb=($config['driver']??'mysql')==='postgresql'?new HSE_PG_DB($config):new HSE_DB($config);
 if(($input['action']??'')==='bootstrap'){HSE_Store::activate();echo wp_json_encode(['data'=>['schema'=>get_option('hse_schema')]]);exit;}
 $request=$input['request'];if(!in_array($request['method']??'GET',['GET','POST','PATCH','DELETE']))throw new HSE_Fault('Metodo non ammesso');
 if(strlen(wp_json_encode($request))>64*1024*1024)throw new HSE_Fault('Richiesta oltre 64 MB',413);
 $files=[];foreach($request['files']??[] as $key=>$file){$bytes=base64_decode($file['base64']??'',true);if($bytes===false||strlen($bytes)>15*1024*1024)throw new HSE_Fault('File oltre 15 MB o non valido');$path=wp_tempnam('upload');$tmp[]=$path;file_put_contents($path,$bytes);$files[$key]=['name'=>$file['name'],'tmp_name'=>$path,'size'=>strlen($bytes),'error'=>UPLOAD_ERR_OK];}
 $result=HSE_API::dispatch(new HSE_Request($request,$files));
 if($result instanceof WP_Error)echo wp_json_encode(['error'=>['message'=>$result->message,'status'=>$result->data['status']??500,'details'=>$result->data['details']??null]]);else {if(isset($result->data['data']['notice']))$result->data['data']['notice']=str_replace('database WordPress','database esterno Streamlit',$result->data['data']['notice']);echo wp_json_encode($result->data);}
}catch(HSE_Fault $e){echo wp_json_encode(['error'=>['message'=>$e->getMessage(),'status'=>$e->status,'details'=>$e->details]]);}
catch(Throwable $e){error_log('HSE Streamlit runtime: '.get_class($e));echo json_encode(['error'=>['message'=>'Operazione non riuscita; dati non confermati','status'=>503]]);}
finally{foreach($tmp as $path)if(is_file($path))unlink($path);}
