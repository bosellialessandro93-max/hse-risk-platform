#!/usr/bin/env bash
set -euo pipefail
HSE_PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HSE_PROJECT_ROOT"
if ! docker network inspect hse-dev >/dev/null 2>&1; then docker network create hse-dev >/dev/null; fi
if docker container inspect hse-db >/dev/null 2>&1; then docker start hse-db >/dev/null; else docker run -d --name hse-db --network hse-dev -e MARIADB_ALLOW_EMPTY_ROOT_PASSWORD=1 -e MARIADB_DATABASE=hse mariadb:11.4@sha256:250e1609e93c0e6aecf64bfbab2d84d5e89d2481540fe77447ff6c855c3b1873 >/dev/null; fi
if docker container inspect hse-wp >/dev/null 2>&1; then docker start hse-wp >/dev/null; else docker run -d --name hse-wp --network hse-dev -p 127.0.0.1:8080:80 -e WORDPRESS_DB_HOST=hse-db -e WORDPRESS_DB_USER=root -e WORDPRESS_DB_PASSWORD= -e WORDPRESS_DB_NAME=hse wordpress:php8.3-apache@sha256:81a34254acaa6ff3b9a67268c2745e9a041c4094cbe5ccd35b75ed3bbdc033b5 >/dev/null; fi
for attempt in {1..30}; do if docker exec hse-db mariadb-admin ping --silent >/dev/null 2>&1; then break; fi; sleep 1; done
docker cp hse-risk-platform/. hse-wp:/var/www/html/wp-content/plugins/hse-risk-platform/
docker exec hse-wp chmod -R a+rX /var/www/html/wp-content/plugins/hse-risk-platform
docker cp tools/bootstrap.php hse-wp:/tmp/hse-bootstrap.php
docker exec hse-wp php /tmp/hse-bootstrap.php
curl --fail --silent 'http://127.0.0.1:8080/?pagename=hse' -o /tmp/hse-readiness.html
python - <<'PY'
from pathlib import Path
assert 'Accedi con il tuo account' in Path('/tmp/hse-readiness.html').read_text()
print('WordPress e shortcode disponibili; login richiesto correttamente.')
PY
