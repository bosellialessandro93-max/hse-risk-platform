<?php
// Local disposable test WordPress only; never run against production.
$qaOrigin=getenv('HSE_QA_ORIGIN')?:'http://127.0.0.1:8080';$_SERVER['HTTP_HOST']=parse_url($qaOrigin,PHP_URL_HOST).':'.(parse_url($qaOrigin,PHP_URL_PORT)?:80);$_SERVER['REQUEST_URI']='/';define('WP_INSTALLING',true);
require '/var/www/html/wp-load.php';
add_filter('pre_wp_mail','__return_false'); // Test bootstrap must not send notifications.
require_once ABSPATH.'wp-admin/includes/upgrade.php';
if(!is_blog_installed()){
 $password=bin2hex(random_bytes(24));
 wp_install('HSE Local QA','hse-admin','hse@example.test',false,'',$password);
 file_put_contents('/tmp/hse-local-auth.json',json_encode(['user'=>'hse-admin','password'=>$password]));
}
update_option('siteurl',$qaOrigin);update_option('home',$qaOrigin);
require_once ABSPATH.'wp-admin/includes/plugin.php';
$result=activate_plugin('hse-risk-platform/hse-risk-platform.php');if(is_wp_error($result)){fwrite(STDERR,$result->get_error_message());exit(1);}
if(!get_page_by_path('hse'))wp_insert_post(['post_title'=>'HSE Workspace','post_name'=>'hse','post_content'=>'[hse_platform]','post_type'=>'page','post_status'=>'publish']);
echo "WordPress installato, plugin attivato\n";
