#!/usr/bin/env bash
# Fresh WordPress database/site on the verified PHP 8.0.30 runtime, without VFS duplication.
set -euo pipefail
cd "$(dirname "$0")/../.."
HSE_PHP80_CONTAINER="${HSE_PHP80_CONTAINER:-hse-wp-php80}"
HSE_PHP80_DB="hse_php8030_zip030_$(date -u +%Y%m%d%H%M%S)"
HSE_PHP80_ROOT=/var/www/hse-zip-030
test -f dist/hse-risk-platform-0.3.0.zip
docker exec hse-db mariadb -e "CREATE DATABASE ${HSE_PHP80_DB};"
docker exec "$HSE_PHP80_CONTAINER" mkdir -p "$HSE_PHP80_ROOT"
docker exec hse-wp tar -C /usr/src/wordpress -cf - . | docker exec -i "$HSE_PHP80_CONTAINER" tar -C "$HSE_PHP80_ROOT" -xf -
HSE_CONFIG_TMP="$(mktemp /tmp/hse-php80-zip-config.XXXXXX)";trap 'rm -f "$HSE_CONFIG_TMP"' EXIT
python - "$HSE_PHP80_DB" "$HSE_CONFIG_TMP" <<'PY'
from pathlib import Path
import sys
s=Path('tools/php80/wp-config.php').read_text().replace("getenv('WORDPRESS_DB_NAME')",repr(sys.argv[1])).replace("$table_prefix='wp_'","$table_prefix='avtest_'")
Path(sys.argv[2]).write_text(s)
PY
docker cp "$HSE_CONFIG_TMP" "$HSE_PHP80_CONTAINER:$HSE_PHP80_ROOT/wp-config.php"
docker exec "$HSE_PHP80_CONTAINER" sh -c 'printf "Alias /zip030 /var/www/hse-zip-030\n<Directory /var/www/hse-zip-030>\nRequire all granted\nAllowOverride All\n</Directory>\n" > /etc/apache2/conf-enabled/hse-zip-030.conf'
docker exec "$HSE_PHP80_CONTAINER" chown -R www-data:www-data "$HSE_PHP80_ROOT"
docker exec "$HSE_PHP80_CONTAINER" apachectl -k graceful
docker cp tools/bootstrap.php "$HSE_PHP80_CONTAINER:/tmp/hse-bootstrap.php"
docker exec -e HSE_QA_ROOT="$HSE_PHP80_ROOT" -e HSE_SKIP_PLUGIN_ACTIVATION=1 -e HSE_QA_ORIGIN=http://127.0.0.1:8084/zip030 -e HSE_QA_AUTH_PATH=/tmp/hse-php80-package-auth.json "$HSE_PHP80_CONTAINER" php /tmp/hse-bootstrap.php
docker cp dist/hse-risk-platform-0.2.0.zip "$HSE_PHP80_CONTAINER:/tmp/hse-package-020.zip"
docker cp dist/hse-risk-platform-0.3.0.zip "$HSE_PHP80_CONTAINER:/tmp/hse-package-030.zip"
docker cp tests/php80-install.php "$HSE_PHP80_CONTAINER:/tmp/hse-php80-install.php"
docker cp tests/package-install.php "$HSE_PHP80_CONTAINER:/tmp/hse-package-test.php"
docker exec -e HSE_QA_ROOT="$HSE_PHP80_ROOT" "$HSE_PHP80_CONTAINER" php /tmp/hse-php80-install.php
docker exec "$HSE_PHP80_CONTAINER" chown -R www-data:www-data "$HSE_PHP80_ROOT"
docker cp "$HSE_PHP80_CONTAINER:/tmp/hse-php80-install-report.json" tests/artifacts/php80-install.json
docker cp "$HSE_PHP80_CONTAINER:/tmp/hse-php80-package-auth.json" .local/php80-package-auth.json
chmod 600 .local/php80-package-auth.json
