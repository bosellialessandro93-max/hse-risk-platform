#!/usr/bin/env bash
set -euo pipefail
HSE_PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HSE_PROJECT_ROOT"
docker cp hse-risk-platform/. hse-wp:/var/www/html/wp-content/plugins/hse-risk-platform/
docker exec hse-wp chmod -R a+rX /var/www/html/wp-content/plugins/hse-risk-platform
docker cp tests/integration.php hse-wp:/tmp/hse-integration.php
docker cp fixtures/. hse-wp:/tmp/hse-fixtures/
if [ -d tests/artifacts ]; then mv tests/artifacts "/tmp/hse-test-artifacts-$(date -u +%Y%m%dT%H%M%S)-$$"; fi
mkdir -p tests/artifacts .local
docker exec hse-wp php /tmp/hse-integration.php > tests/artifacts/integration.txt
cat tests/artifacts/integration.txt
docker cp tests/timezone.php hse-wp:/tmp/hse-timezone.php
docker exec hse-wp php /tmp/hse-timezone.php
docker cp hse-wp:/tmp/hse-test-ids.json .local/ids.json
docker cp hse-wp:/tmp/hse-local-auth.json .local/auth.json
chmod 600 .local/auth.json
