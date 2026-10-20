<?php
require '/var/www/html/wp-load.php';
if(HSE_Domain::today('Y-m-d',strtotime('2026-09-30T22:30:00Z'))!=='2026-10-01')throw new RuntimeException('Europe/Rome month boundary');
if(HSE_Domain::today('Y-m-d',strtotime('2026-10-24T22:30:00Z'))!=='2026-10-25')throw new RuntimeException('Europe/Rome DST date');
echo "PASS Europe/Rome confine mese e cambio ora\n";
