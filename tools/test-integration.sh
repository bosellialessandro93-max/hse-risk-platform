#!/usr/bin/env bash
set -euo pipefail
HSE_PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HSE_PROJECT_ROOT"
HSE_TEST_CONTAINER="${HSE_TEST_CONTAINER:-hse-wp}"
docker cp hse-risk-platform/. ${HSE_TEST_CONTAINER}:/var/www/html/wp-content/plugins/hse-risk-platform/
docker exec "$HSE_TEST_CONTAINER" chmod -R a+rX /var/www/html/wp-content/plugins/hse-risk-platform
docker cp tests/integration.php ${HSE_TEST_CONTAINER}:/tmp/hse-integration.php
docker cp fixtures/. ${HSE_TEST_CONTAINER}:/tmp/hse-fixtures/
if [ -d tests/artifacts ]; then mv tests/artifacts "/tmp/hse-test-artifacts-$(date -u +%Y%m%dT%H%M%S)-$$"; fi
mkdir -p tests/artifacts .local
docker exec "$HSE_TEST_CONTAINER" php /tmp/hse-integration.php > tests/artifacts/integration.txt
cat tests/artifacts/integration.txt
docker cp tests/timezone.php ${HSE_TEST_CONTAINER}:/tmp/hse-timezone.php
docker exec "$HSE_TEST_CONTAINER" php /tmp/hse-timezone.php
docker cp ${HSE_TEST_CONTAINER}:/tmp/hse-test-ids.json .local/ids.json
docker cp ${HSE_TEST_CONTAINER}:/tmp/hse-local-auth.json .local/auth.json
chmod 600 .local/auth.json
