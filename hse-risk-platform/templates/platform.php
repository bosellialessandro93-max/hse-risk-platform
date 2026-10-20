<?php
/** Standalone page template: WordPress hooks retained, theme chrome excluded on this page only. */
if (!defined('ABSPATH')) exit;
?><!doctype html>
<html <?php language_attributes(); ?>>
<head><meta charset="<?php bloginfo('charset'); ?>"><meta name="viewport" content="width=device-width, initial-scale=1"><?php wp_head(); ?></head>
<body <?php body_class('hse-app-page'); ?>>
<?php wp_body_open(); ?>
<div class="hse-app-canvas">
<?php while (have_posts()) { the_post(); the_content(); } ?>
</div>
<?php wp_footer(); ?>
</body></html>
