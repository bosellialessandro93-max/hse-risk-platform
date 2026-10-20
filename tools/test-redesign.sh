#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
HSE_TEST_CONTAINER="${HSE_TEST_CONTAINER:-hse-wp}"
docker cp tests/redesign-setup.php "$HSE_TEST_CONTAINER:/tmp/hse-redesign-setup.php"
docker exec "$HSE_TEST_CONTAINER" php /tmp/hse-redesign-setup.php
docker cp "$HSE_TEST_CONTAINER:/tmp/hse-redesign-auth.json" .local/redesign-auth.json
chmod 600 .local/redesign-auth.json
node tests/redesign.mjs
