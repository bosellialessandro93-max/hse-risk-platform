<?php
if(PHP_VERSION!=='8.0.30'||extension_loaded('zip'))throw new RuntimeException('Expected PHP 8.0.30 without ZIP for this negative test');
require '/var/www/html/wp-load.php';wp_set_current_user(1);
class HSE_ExpectedActivationStop extends RuntimeException{}
add_filter('wp_die_handler',function(){return function($message){throw new HSE_ExpectedActivationStop(strip_tags($message));};});
global $wpdb;$before=(int)$wpdb->get_var('SELECT COUNT(*) FROM '.HSE_Store::table());
try{HSE_Store::activate();throw new RuntimeException('Missing ZIP was accepted');}catch(HSE_ExpectedActivationStop $e){if(stripos($e->getMessage(),'zip')===false)throw $e;}
if((int)$wpdb->get_var('SELECT COUNT(*) FROM '.HSE_Store::table())!==$before)throw new RuntimeException('Failed activation changed records');
echo 'PASS PHP 8.0.30: missing ZIP rejected with explicit hosting requirement, records unchanged'.PHP_EOL;
