<?php
if(!defined('ABSPATH'))exit;
class HSE_Elementor_Widget extends \Elementor\Widget_Base {
 public function get_name(){return 'hse-risk-platform';}
 public function get_title(){return 'HSE Risk Platform';}
 public function get_icon(){return 'eicon-site-identity';}
 public function get_categories(){return ['general'];}
 protected function render(){echo do_shortcode('[hse_platform]');}
}
