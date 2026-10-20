#!/usr/bin/env bash
# Dedicated synthetic DB and container. Never reads production configuration.
set -euo pipefail
cd "$(dirname "$0")/.."
test -f dist/hse-risk-platform-0.2.0.zip
docker exec hse-db mariadb -e 'CREATE DATABASE IF NOT EXISTS hse_zip_020_final;'
if docker container inspect hse-wp-zip-020-final >/dev/null 2>&1; then docker start hse-wp-zip-020-final >/dev/null; else
 docker run -d --name hse-wp-zip-020-final --network hse-dev -p 127.0.0.1:8083:80 -e WORDPRESS_DB_HOST=hse-db -e WORDPRESS_DB_USER=root -e WORDPRESS_DB_PASSWORD= -e WORDPRESS_DB_NAME=hse_zip_020_final wordpress:php8.3-apache@sha256:81a34254acaa6ff3b9a67268c2745e9a041c4094cbe5ccd35b75ed3bbdc033b5 >/dev/null
fi
for attempt in {1..30}; do if docker exec hse-wp-zip-020-final test -f /var/www/html/wp-load.php; then break; fi; sleep 1; done
docker cp dist/hse-risk-platform-0.2.0.zip hse-wp-zip-020-final:/tmp/hse-install.zip
docker exec hse-wp-zip-020-final php -r '$z=new ZipArchive();if($z->open("/tmp/hse-install.zip")!==true||!$z->extractTo("/var/www/html/wp-content/plugins"))exit(1);$z->close();'
docker cp tools/bootstrap.php hse-wp-zip-020-final:/tmp/hse-bootstrap.php
docker exec -e HSE_QA_ORIGIN=http://127.0.0.1:8083 hse-wp-zip-020-final php /tmp/hse-bootstrap.php
docker cp tests/package-install.php hse-wp-zip-020-final:/tmp/hse-package-test.php
docker exec hse-wp-zip-020-final php /tmp/hse-package-test.php
curl --fail --silent 'http://127.0.0.1:8083/?pagename=hse' -o /tmp/hse-zip-shortcode.html
python - <<'PY'
from pathlib import Path
assert 'Accedi con il tuo account' in Path('/tmp/hse-zip-shortcode.html').read_text()
print('PASS installazione ZIP e shortcode pubblico protetto')
PY
