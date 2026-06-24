#!/usr/bin/env bash
# Capture store-ready screenshots from the running SPA using the existing
# Puppeteer harness in frontend/scripts/screenshot.mjs. Outputs are written
# into store-meta/{appstore,playstore}/screenshots/.
#
# Prerequisites:
#   - Backend running with seeded demo data
#   - Frontend dev server running on http://localhost:5173
#
# Usage:
#   scripts/generate-screenshots.sh [appstore|playstore|all]

set -euo pipefail
TARGET="${1:-all}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cd "$REPO_ROOT/frontend"
node scripts/screenshot.mjs --output "$REPO_ROOT/store-meta/$TARGET/screenshots"
echo "Screenshots written under store-meta/$TARGET/screenshots/"
