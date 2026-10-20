<?php
/**
 * Plugin Name: HSE Risk Platform
 * Description: Workspace HSE autonomo: cantieri, valutazioni, sinottici, coordinamento e mappe.
 * Version: 0.2.0
 * Requires at least: 6.6
 * Requires PHP: 8.1
 * License: GPL-2.0-or-later
 * Text Domain: hse-risk-platform
 */
if (!defined('ABSPATH')) exit;
define('HSE_VERSION', '0.2.0');
define('HSE_DIR', __DIR__);
require_once __DIR__.'/includes/store.php';
require_once __DIR__.'/includes/domain.php';
require_once __DIR__.'/includes/risk.php';
require_once __DIR__.'/includes/maps.php';
require_once __DIR__.'/includes/api.php';
register_activation_hook(__FILE__, ['HSE_Store','migrate']);
add_action('plugins_loaded', function(){ if(get_option('hse_schema') !== '1') HSE_Store::migrate(); });
add_action('rest_api_init', ['HSE_API','routes']);
add_action('template_redirect', function(){
 if(is_singular() && has_shortcode(get_post()->post_content ?? '', 'hse_platform')) {
  if(!defined('DONOTCACHEPAGE')) define('DONOTCACHEPAGE',true);
  nocache_headers(); header('X-Robots-Tag: noindex, nofollow');
 }
});
add_action('wp_enqueue_scripts',function(){if(is_singular() && has_shortcode(get_post()->post_content??'', 'hse_platform'))wp_enqueue_style('hse-platform',plugins_url('assets/app.css',__FILE__),[],HSE_VERSION);});
add_shortcode('hse_platform', function(){
 if(!is_user_logged_in()) return '<p>Accedi con il tuo account WordPress: <a href="'.esc_url(wp_login_url(get_permalink())).'">Accedi</a></p>';
 wp_enqueue_style('hse-platform',plugins_url('assets/app.css',__FILE__),[],HSE_VERSION);
 wp_enqueue_script('hse-platform',plugins_url('assets/app.bundle.js',__FILE__),[],HSE_VERSION,true);
 wp_add_inline_script('hse-platform','window.HSE_CONFIG='.wp_json_encode(['api'=>rest_url('hse/v1/'),'nonce'=>wp_create_nonce('wp_rest'),'assets'=>plugins_url('assets/',__FILE__),'admin'=>current_user_can('manage_options'),'user'=>get_current_user_id()]).';','before');
 return '<div class="hse-platform" id="hse-platform"><p role="status">Caricamento HSE Risk Platform…</p></div>';
});

add_action('elementor/widgets/register',function($manager){
 if(!class_exists('\Elementor\Widget_Base'))return;
 require_once HSE_DIR.'/includes/elementor.php';
 $manager->register(new HSE_Elementor_Widget());
});
