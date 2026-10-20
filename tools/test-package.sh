#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
bash tools/php80/test-package.sh
