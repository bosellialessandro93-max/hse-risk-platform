<?php
require '/var/www/html/wp-load.php';wp_set_current_user(1);
$page=get_page_by_path('hse');update_post_meta($page->ID,'_wp_page_template','hse-platform-full-width.php');
if(!isset(wp_get_theme()->get_page_templates($page)['hse-platform-full-width.php']))throw new RuntimeException('Dedicated template absent');
$ids=json_decode(file_get_contents('/tmp/hse-test-ids.json'),true);$site=HSE_Store::get($ids['site_id']);
$company=HSE_Store::list('companies',$site['id'])[0]??null;
$users=[];foreach(['manager','reader','company'] as $role){$pass=wp_generate_password(32);$login='redesign-'.$role.'-'.wp_generate_uuid4();$uid=wp_insert_user(['user_login'=>$login,'user_pass'=>$pass,'role'=>'subscriber']);if(is_wp_error($uid))throw new RuntimeException($uid->get_error_message());HSE_Store::save('memberships',['site_id'=>$site['id'],'user_id'=>$uid,'role'=>$role,'company_id'=>$role==='company'?$company['id']:'','share_plans'=>true]);$users[$role]=['user'=>$login,'password'=>$pass];}
file_put_contents('/tmp/hse-redesign-auth.json',wp_json_encode($users));echo 'PASS dedicated template and synthetic role users prepared on test site'.PHP_EOL;
