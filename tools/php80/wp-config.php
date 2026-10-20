<?php
// Test-only configuration. No production data or credentials.
define('DB_NAME',getenv('WORDPRESS_DB_NAME'));
define('DB_USER','root');define('DB_PASSWORD','');define('DB_HOST','hse-db');
define('DB_CHARSET','utf8mb4');define('DB_COLLATE','');$table_prefix='wp_';
define('WP_DEBUG',true);define('WP_DEBUG_LOG',true);define('WP_DEBUG_DISPLAY',false);
define('WP_ENVIRONMENT_TYPE','local');define('FS_METHOD','direct');
define('WP_HTTP_BLOCK_EXTERNAL',true);define('AUTOMATIC_UPDATER_DISABLED',true);define('DISABLE_WP_CRON',true);
if(!defined('ABSPATH'))define('ABSPATH',__DIR__.'/');
require_once ABSPATH.'wp-settings.php';
