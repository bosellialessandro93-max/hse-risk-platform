#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
bash tools/php80/prepare.sh
docker cp tests/php80-compat.php hse-wp-php80:/tmp/hse-php80-compat.php
docker exec hse-wp-php80 php /tmp/hse-php80-compat.php
docker cp tests/php80-missing-zip.php hse-wp-php80:/tmp/hse-php80-missing-zip.php
docker exec hse-wp-php80 php -n -d extension=mysqli /tmp/hse-php80-missing-zip.php
HSE_TEST_CONTAINER=hse-wp-php80 HSE_EXPECT_PHP=8.0.30 HSE_TEST_URL=http://127.0.0.1:8084 npm test
python tests/validate_exports.py
python tools/package.py
bash tools/php80/test-package.sh
HSE_TEST_PACKAGE_FILE="$PWD/dist/hse-risk-platform-0.2.1.zip" node tests/php80-web.mjs
