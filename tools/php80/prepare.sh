#!/usr/bin/env bash
# Dedicated disposable PHP 8.0.30 + WordPress runtime; does not replace hse-wp.
set -euo pipefail
cd "$(dirname "$0")/../.."
HSE_PHP80_CONTAINER="${HSE_PHP80_CONTAINER:-hse-wp-php80}"
HSE_PHP80_DB="${HSE_PHP80_DB:-hse_php8030_021}"
HSE_PHP80_PORT="${HSE_PHP80_PORT:-8084}"
HSE_WORDPRESS_SOURCE="${HSE_WORDPRESS_SOURCE:-hse-wp}"
[[ "$HSE_PHP80_DB" =~ ^hse_php8030_[a-zA-Z0-9_]+$ ]] || exit 1
[[ "$HSE_PHP80_PORT" =~ ^[0-9]+$ ]] || exit 1
docker exec hse-db mariadb -e "CREATE DATABASE IF NOT EXISTS ${HSE_PHP80_DB};"
if docker container inspect "$HSE_PHP80_CONTAINER" >/dev/null 2>&1; then docker start "$HSE_PHP80_CONTAINER" >/dev/null; else
 docker run -d --name "$HSE_PHP80_CONTAINER" --network hse-dev -p "127.0.0.1:${HSE_PHP80_PORT}:80" -e "WORDPRESS_DB_NAME=$HSE_PHP80_DB" php:8.0.30-apache@sha256:c87b4c94d53b35520467b6d026f38656ab9a6d446fa3a0fbba1bc633125f9ad2 >/dev/null
fi
docker exec "$HSE_PHP80_CONTAINER" php -r 'if(PHP_VERSION!=="8.0.30")exit(1);echo "PHP ".PHP_VERSION.PHP_EOL;'
if ! docker exec "$HSE_PHP80_CONTAINER" php -r 'exit(extension_loaded("mysqli")&&extension_loaded("zip")?0:1);'; then
 HSE_PHP80_DEBS="$(mktemp -d /tmp/hse-php80-debs.XXXXXX)";trap 'rm -rf "$HSE_PHP80_DEBS"' EXIT
 curl --fail --silent --show-error https://deb.debian.org/debian/pool/main/libz/libzip/libzip4_1.7.3-1_amd64.deb -o "$HSE_PHP80_DEBS/libzip4.deb"
 curl --fail --silent --show-error https://deb.debian.org/debian/pool/main/libz/libzip/libzip-dev_1.7.3-1_amd64.deb -o "$HSE_PHP80_DEBS/libzip-dev.deb"
 curl --fail --silent --show-error https://deb.debian.org/debian/pool/main/z/zlib/zlib1g-dev_1.2.11.dfsg-2+deb11u2_amd64.deb -o "$HSE_PHP80_DEBS/zlib1g-dev.deb"
 (cd "$HSE_PHP80_DEBS";sha256sum -c <<'SUMS'
d68fa92aa7a40aa6f2880c54768dcb0b6fba47ad38ba73b9336d8ecd83bb1edb  libzip4.deb
07f80e277aa1cb4492413ff8cf96512b0ee58a7d922b98f0f965b632a71aeb83  libzip-dev.deb
f49fc849870c4e64fed2794722841ee950c1788f7fe90b3a091e6a098a46cd33  zlib1g-dev.deb
SUMS
 )
 docker cp "$HSE_PHP80_DEBS/." "$HSE_PHP80_CONTAINER:/tmp/hse-debs/"
 docker exec "$HSE_PHP80_CONTAINER" sh -c 'dpkg -i /tmp/hse-debs/zlib1g-dev.deb /tmp/hse-debs/libzip4.deb /tmp/hse-debs/libzip-dev.deb && docker-php-ext-install -j2 mysqli zip && rm -r /tmp/hse-debs' > /tmp/hse-php80-extensions.log 2>&1
fi
if ! docker exec "$HSE_PHP80_CONTAINER" test -f /var/www/html/wp-load.php; then
 docker exec "$HSE_WORDPRESS_SOURCE" tar -C /usr/src/wordpress -cf - . | docker exec -i "$HSE_PHP80_CONTAINER" tar -C /var/www/html -xf -
fi
docker cp tools/php80/wp-config.php "$HSE_PHP80_CONTAINER:/var/www/html/wp-config.php"
docker exec "$HSE_PHP80_CONTAINER" sh -c "printf 'memory_limit=256M\nupload_max_filesize=32M\npost_max_size=48M\nlog_errors=On\n' > /usr/local/etc/php/conf.d/hse-test.ini"
docker exec "$HSE_PHP80_CONTAINER" chown -R www-data:www-data /var/www/html
docker exec "$HSE_PHP80_CONTAINER" a2enmod rewrite >/dev/null
docker restart "$HSE_PHP80_CONTAINER" >/dev/null
for attempt in {1..30}; do if curl --fail --silent "http://127.0.0.1:${HSE_PHP80_PORT}/wp-admin/install.php" -o /dev/null; then break; fi; sleep 1; done
curl --fail --silent "http://127.0.0.1:${HSE_PHP80_PORT}/wp-admin/install.php" -o /dev/null
if [ "${HSE_PHP80_CORE_ONLY:-0}" != 1 ]; then
 docker cp hse-risk-platform/. "$HSE_PHP80_CONTAINER:/var/www/html/wp-content/plugins/hse-risk-platform/"
 docker exec "$HSE_PHP80_CONTAINER" chmod -R a+rX /var/www/html/wp-content/plugins/hse-risk-platform
fi
docker cp tools/bootstrap.php "$HSE_PHP80_CONTAINER:/tmp/hse-bootstrap.php"
docker exec -e "HSE_QA_ORIGIN=http://127.0.0.1:${HSE_PHP80_PORT}" -e "HSE_SKIP_PLUGIN_ACTIVATION=${HSE_PHP80_CORE_ONLY:-0}" "$HSE_PHP80_CONTAINER" php /tmp/hse-bootstrap.php
