<?php
// Run inside the real PHP 8.0.30 WordPress container, never against production.
if(PHP_VERSION!=='8.0.30')throw new RuntimeException('Wrong test runtime: '.PHP_VERSION);
require '/var/www/html/wp-load.php';require_once ABSPATH.'wp-admin/includes/plugin.php';require_once ABSPATH.'wp-admin/includes/file.php';require_once ABSPATH.'wp-admin/includes/upgrade.php';wp_set_current_user(1);
$plugin='hse-risk-platform/hse-risk-platform.php';$header=get_plugin_data(WP_PLUGIN_DIR.'/'.$plugin,false,false);
if($header['Version']!=='0.3.0'||$header['RequiresPHP']!=='8.0.30')throw new RuntimeException('Unexpected plugin metadata');
$requirements=validate_plugin_requirements($plugin);if(is_wp_error($requirements))throw new RuntimeException($requirements->get_error_message());
$files=array_merge([HSE_DIR.'/hse-risk-platform.php',HSE_DIR.'/uninstall.php'],glob(HSE_DIR.'/includes/*.php'),glob(HSE_DIR.'/templates/*.php'));$functions=[];
foreach($files as $file){$tokens=token_get_all(file_get_contents($file),TOKEN_PARSE);$tokens=array_values(array_filter($tokens,fn($t)=>!is_array($t)||!in_array($t[0],[T_WHITESPACE,T_COMMENT,T_DOC_COMMENT])));
 foreach($tokens as $i=>$t){if(!is_array($t)||$t[0]!==T_STRING||($tokens[$i+1]??null)!=='(')continue;$previous=$tokens[$i-1]??null;if(is_array($previous)&&in_array($previous[0],[T_OBJECT_OPERATOR,T_DOUBLE_COLON,T_FUNCTION,T_NEW]))continue;$name=$t[1];$functions[$name]=true;if(!function_exists($name))throw new RuntimeException('Unavailable PHP/WordPress function: '.$name.' in '.basename($file));}}
foreach(['mysqli','mbstring','fileinfo','simplexml','zip'] as $ext)if(!extension_loaded($ext))throw new RuntimeException('Missing extension '.$ext);
foreach(['ZipArchive','finfo','SimpleXMLElement','DateTimeZone'] as $class)if(!class_exists($class))throw new RuntimeException('Missing runtime class '.$class);
global $wpdb;$tables=[];foreach(['records','revisions','requests','assets'] as $suffix){$table=HSE_Store::table($suffix);$status=$wpdb->get_row($wpdb->prepare('SHOW TABLE STATUS WHERE Name=%s',$table),ARRAY_A);if(!$status||$status['Engine']!=='InnoDB')throw new RuntimeException('Table missing or nontransactional: '.$table);$tables[]=$table;}
$report=['php'=>PHP_VERSION,'sapi'=>PHP_SAPI,'wordpress'=>get_bloginfo('version'),'plugin'=>$header['Version'],'files_parsed'=>count($files),'global_functions_verified'=>count($functions),'tables'=>$tables,'wordpress_includes'=>['file.php','upgrade.php']];
$report['required_extensions']=array_fill_keys(['mysqli','mbstring','fileinfo','simplexml','zip'],true);$report['gd_available']=extension_loaded('gd');$report['functions']=array_keys($functions);sort($report['functions']);
file_put_contents('/tmp/hse-php80-audit.json',wp_json_encode($report,JSON_PRETTY_PRINT));
echo 'PASS PHP '.PHP_VERSION.': '.count($files).' file parsed, '.count($functions).' global functions available, 4 InnoDB tables and WordPress requirements satisfied'.PHP_EOL;
