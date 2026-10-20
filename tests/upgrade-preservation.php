<?php
/** Local synthetic-site upgrade evidence; no production connection. */
require (getenv('HSE_QA_ROOT')?:'/var/www/hse-zip-021').'/wp-load.php';
global $wpdb;$keys=['records'=>'id','revisions'=>'id','requests'=>'request_key','assets'=>'id'];$file='/tmp/hse-upgrade-row-hashes.json';
if(getenv('HSE_UPGRADE_PHASE')==='baseline'){
 if(HSE_VERSION!=='0.2.1')throw new RuntimeException('Expected 0.2.1 baseline');$snapshot=[];
 foreach($keys as $kind=>$key){$rows=$wpdb->get_results('SELECT * FROM '.HSE_Store::table($kind).' ORDER BY '.$key,ARRAY_A);if($wpdb->last_error)throw new RuntimeException($wpdb->last_error);$snapshot[$kind]=[];foreach($rows as $row)$snapshot[$kind][$row[$key]]=hash('sha256',serialize($row));}
 file_put_contents($file,wp_json_encode(['version'=>HSE_VERSION,'schema'=>get_option('hse_schema'),'tables'=>$snapshot]));echo 'PASS upgrade baseline 0.2.1, four tables including binary assets'.PHP_EOL;return;
}
$before=json_decode(file_get_contents($file),true);if(HSE_VERSION!=='0.3.0'||get_option('hse_schema')!==$before['schema'])throw new RuntimeException('Unexpected version/schema after upgrade');$counts=[];
foreach($keys as $kind=>$key){$counts[$kind]=0;foreach($before['tables'][$kind] as $id=>$hash){$row=$wpdb->get_row($wpdb->prepare('SELECT * FROM '.HSE_Store::table($kind).' WHERE '.$key.'=%s',$id),ARRAY_A);if(!$row||hash('sha256',serialize($row))!==$hash)throw new RuntimeException('Original row lost or modified: '.$kind);$counts[$kind]++;}}
$linked=0;foreach(array_keys($before['tables']['records']) as $id){$record=HSE_Store::get($id);foreach($record['attachments']??[] as $asset)if(isset($before['tables']['assets'][$asset]))$linked++;}if(!$linked)throw new RuntimeException('Upgrade photo-link precondition not exercised');
$report=['linked_original_private_images'=>$linked,'php'=>PHP_VERSION,'from'=>$before['version'],'to'=>HSE_VERSION,'schema'=>get_option('hse_schema'),'existing_rows_byte_identical'=>$counts,'additional_http_test_records_allowed'=>true];file_put_contents('/tmp/hse-upgrade-report.json',wp_json_encode($report,JSON_PRETTY_PRINT));echo 'PASS 0.2.1 → 0.3.0: all original rows including assets, revisions and idempotency preserved: '.wp_json_encode($counts).PHP_EOL;
