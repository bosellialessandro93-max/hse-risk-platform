<?php
/** Narrow compatibility boundary for the existing, unchanged HSE domain modules. */
define('ARRAY_A','ARRAY_A');
function wp_json_encode($value,$flags=0){return json_encode($value,$flags|JSON_THROW_ON_ERROR);}
function wp_generate_uuid4(){$b=random_bytes(16);$b[6]=chr((ord($b[6])&15)|64);$b[8]=chr((ord($b[8])&63)|128);$h=bin2hex($b);return substr($h,0,8).'-'.substr($h,8,4).'-'.substr($h,12,4).'-'.substr($h,16,4).'-'.substr($h,20);}
function wp_is_uuid($value){return is_string($value)&&preg_match('/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/iD',$value)===1;}
function get_current_user_id(){return (int)$GLOBALS['hse_actor']['id'];}
function current_user_can($capability){return $capability==='manage_options'&&!empty($GLOBALS['hse_actor']['is_admin']);}
function is_user_logged_in(){return get_current_user_id()>0;}
function get_userdata($id){global $wpdb;return $wpdb->get_row($wpdb->prepare('SELECT id FROM '.$wpdb->prefix.'users WHERE id=%d AND active=1',$id),ARRAY_A);}
function get_option($key,$default=false){global $wpdb;$row=$wpdb->get_row($wpdb->prepare('SELECT value FROM '.$wpdb->prefix.'options WHERE name=%s',$key),ARRAY_A);return $row?json_decode($row['value'],true):$default;}
function update_option($key,$value,$autoload=false){global $wpdb;$wpdb->query($wpdb->prepare('INSERT INTO '.$wpdb->prefix.'options (name,value) VALUES (%s,%s) ON DUPLICATE KEY UPDATE value=VALUES(value)',$key,wp_json_encode($value)));return true;}
function add_role(...$ignored){return null;}
function wp_date($format,$timestamp=null,$timezone=null){$date=new DateTimeImmutable('@'.($timestamp??time()));return $date->setTimezone($timezone??new DateTimeZone('Europe/Rome'))->format($format);}
function sanitize_textarea_field($value){$value=mb_convert_encoding((string)$value,'UTF-8','UTF-8');return trim(preg_replace('/%[a-f0-9]{2}/i','',strip_tags($value)));}
function sanitize_text_field($value){return preg_replace('/[\r\n\t ]+/',' ',sanitize_textarea_field($value));}
function sanitize_file_name($value){$value=basename(str_replace('\\','/',(string)$value));return preg_replace('/[^\pL\pN._ -]/u','_', $value)?:'allegato';}
function esc_html($value){return htmlspecialchars($value,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8');}
function wp_die($message){throw new RuntimeException(strip_tags($message));}
function wp_tempnam($name){$file=tempnam(sys_get_temp_dir(),'hse-');if($file===false)throw new RuntimeException('Temporary processing unavailable');return $file;}
function is_ssl(){return getenv('HSE_TLS_ORIGIN')!=='0';}
function get_bloginfo($field){return 'Streamlit standalone (WordPress non richiesto)';}
function wp_max_upload_size(){return 15*1024*1024;}
function register_rest_route(...$ignored){}
function dbDelta($sql){global $wpdb;$sql=preg_replace('/^CREATE TABLE /','CREATE TABLE IF NOT EXISTS ',$sql);if($wpdb->query($sql)===false)throw new RuntimeException('Database schema unavailable');}
class WP_Error {
 public $code;public $message;public $data;
 function __construct($code,$message,$data=[]){$this->code=$code;$this->message=$message;$this->data=$data;}
}
class WP_REST_Response {public $data;public $status;function __construct($data,$status=200){$this->data=$data;$this->status=$status;}function header(...$ignored){}}
class HSE_Request implements ArrayAccess {
 private $route;private $method;private $data;private $params;private $files;
 function __construct($request,$files){$pieces=explode('?', $request['path'],2);$this->route=trim($pieces[0],'/');parse_str($pieces[1]??'',$query);$this->method=$request['method']??'GET';$this->data=$request['data']??[];$this->params=array_merge($query,$request['form']??[],$this->data);$this->files=$files;}
 function get_body(){return wp_json_encode($this->data);}
 function get_json_params(){return $this->data;}
 function get_params(){return $this->params;}
 function get_param($key){return $this->params[$key]??null;}
 function get_method(){return $this->method;}
 function get_file_params(){return $this->files;}
 public function offsetExists($key):bool{return $key==='path';}
 public function offsetGet($key):mixed{return $key==='path'?$this->route:null;}
 public function offsetSet($key,$value):void{throw new LogicException('Immutable request');}
 public function offsetUnset($key):void{throw new LogicException('Immutable request');}
}
class HSE_DB {
 public $prefix;public $last_error='';private $db;
 function __construct($config){
  $this->prefix=$config['prefix']??'st_';if(!preg_match('/^[a-zA-Z][a-zA-Z0-9_]{0,30}$/D',$this->prefix))throw new RuntimeException('Invalid database prefix');
  mysqli_report(MYSQLI_REPORT_OFF);$this->db=mysqli_init();$this->db->options(MYSQLI_OPT_CONNECT_TIMEOUT,10);$ca=null;$flags=0;
  try{if($config['tls']??true){if(!empty($config['ca_certificate'])){$ca=wp_tempnam('ca');file_put_contents($ca,$config['ca_certificate']);}$this->db->ssl_set(null,null,$ca,null,null);$this->db->options(MYSQLI_OPT_SSL_VERIFY_SERVER_CERT,true);$flags=MYSQLI_CLIENT_SSL;}
   if(!@$this->db->real_connect($config['host'],$config['user'],$config['password'],$config['name'],(int)($config['port']??3306),null,$flags))throw new RuntimeException('External database connection unavailable');
  }finally{if($ca)unlink($ca);}
  $this->db->set_charset('utf8mb4');$this->query("SET SESSION sql_mode='STRICT_ALL_TABLES,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO'");
 }
 function get_charset_collate(){return 'DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci';}
 function prepare($sql,...$args){if(count($args)===1&&is_array($args[0]))$args=$args[0];$i=0;return preg_replace_callback('/%[sdf]/',function($m)use(&$i,$args){if(!array_key_exists($i,$args))throw new RuntimeException('Invalid SQL arguments');$v=$args[$i++];return $m[0]==='%d'?(string)(int)$v:($m[0]==='%f'?(string)(float)$v:"'".$this->db->real_escape_string((string)$v)."'");},$sql);}
 function query($sql){$r=$this->db->query($sql);$this->last_error=$this->db->error;return $r===false?false:($r instanceof mysqli_result?$r:$this->db->affected_rows);}
 function get_results($sql,$format=ARRAY_A){$r=$this->query($sql);if(!$r instanceof mysqli_result)throw new RuntimeException('Database query failed');return $r->fetch_all(MYSQLI_ASSOC);}
 function get_row($sql,$format=ARRAY_A){return $this->get_results($sql,$format)[0]??null;}
 function get_var($sql){$row=$this->get_row($sql);return $row?array_values($row)[0]:null;}
 function insert($table,$row,$formats=null){$keys=array_keys($row);$sql='INSERT INTO '.$table.' (`'.implode('`,`',$keys).'`) VALUES ('.implode(',',array_fill(0,count($keys),'%s')).')';return $this->query($this->prepare($sql,array_values($row)));}
 function update($table,$row,$where,$formats=null,$whereFormats=null){$sets=[];$args=[];foreach($row as $key=>$value){$sets[]='`'.$key.'`=%s';$args[]=$value;}$conditions=[];foreach($where as $key=>$value){$conditions[]='`'.$key.'`=%s';$args[]=$value;}return $this->query($this->prepare('UPDATE '.$table.' SET '.implode(',',$sets).' WHERE '.implode(' AND ',$conditions),$args));}
}
