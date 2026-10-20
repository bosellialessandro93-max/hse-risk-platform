<?php
if(PHP_VERSION!=='8.0.30')throw new RuntimeException('Expected exact PHP 8.0.30');
require (getenv('HSE_QA_ROOT')?:'/var/www/hse-zip-030').'/wp-load.php';wp_set_current_user(1);
require_once ABSPATH.'wp-admin/includes/file.php';require_once ABSPATH.'wp-admin/includes/plugin.php';require_once ABSPATH.'wp-admin/includes/class-wp-upgrader.php';
global $wpdb;$before=$wpdb->get_col($wpdb->prepare('SHOW TABLES LIKE %s',$wpdb->esc_like($wpdb->prefix.'hse_').'%'));if($before)throw new RuntimeException('Fresh test must start without plugin tables');
$skin=new WP_Ajax_Upgrader_Skin();$upgrader=new Plugin_Upgrader($skin);ob_start();$old=$upgrader->install('/tmp/hse-package-020.zip');ob_end_clean();$oldError=is_wp_error($old)?$old:(is_wp_error($skin->result)?$skin->result:$skin->get_errors());
if(!is_wp_error($oldError)||!in_array('incompatible_php_required_version',$oldError->get_error_codes()))throw new RuntimeException('Previous ZIP did not reproduce PHP 8.1 requirement: '.wp_json_encode($oldError));
echo 'PASS WordPress installer rejects previous ZIP 0.2.0: incompatible_php_required_version'.PHP_EOL;
$skin=new WP_Ajax_Upgrader_Skin();$upgrader=new Plugin_Upgrader($skin);ob_start();$new=$upgrader->install('/tmp/hse-package-030.zip');ob_end_clean();if($new!==true)throw new RuntimeException('ZIP installation failed: '.wp_json_encode(is_wp_error($new)?$new:$skin->get_errors()));
$activation=activate_plugin('hse-risk-platform/hse-risk-platform.php');if(is_wp_error($activation))throw new RuntimeException($activation->get_error_message());
$engines=[];foreach(['records','revisions','requests','assets'] as $suffix){$table=HSE_Store::table($suffix);$status=$wpdb->get_row($wpdb->prepare('SHOW TABLE STATUS WHERE Name=%s',$table),ARRAY_A);if(!$status||$status['Engine']!=='InnoDB')throw new RuntimeException('Table creation failed: '.$table);$engines[$table]=$status['Engine'];}
require __DIR__.'/hse-package-test.php';
$report=['php'=>PHP_VERSION,'wordpress'=>get_bloginfo('version'),'plugin'=>HSE_VERSION,'installer'=>'WordPress Plugin_Upgrader','previous_zip_error'=>$oldError->get_error_codes(),'fresh_database'=>true,'tables_before'=>count($before),'tables_after'=>count($engines),'table_engines'=>$engines,'sha256'=>hash_file('sha256','/tmp/hse-package-030.zip'),'activation'=>is_plugin_active('hse-risk-platform/hse-risk-platform.php'),'preservation_after_reactivation'=>true];file_put_contents('/tmp/hse-php80-install-report.json',wp_json_encode($report,JSON_PRETTY_PRINT));
echo 'PASS PHP 8.0.30: WordPress ZIP installer, activation, 4 fresh InnoDB tables, nondefault prefix and data preservation'.PHP_EOL;
