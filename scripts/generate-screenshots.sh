#!/usr/bin/env bash
# Capture store-ready screenshots from the running SPA.
#
# Prerequisites:
#   - docker compose up --build   (or backend + frontend dev server)
#   - CHROME_PATH set to installed Chrome
#
# Usage:
#   scripts/generate-screenshots.sh [appstore|playstore|all]

set -euo pipefail
TARGET="${1:-all}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ -z "${CHROME_PATH:-}" ]; then
  if [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    export CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  elif [ -f "/c/Program Files/Google/Chrome/Application/chrome.exe" ]; then
    export CHROME_PATH="/c/Program Files/Google/Chrome/Application/chrome.exe"
  elif [ -f "C:/Program Files/Google/Chrome/Application/chrome.exe" ]; then
    export CHROME_PATH="C:/Program Files/Google/Chrome/Application/chrome.exe"
  else
    echo "Set CHROME_PATH to your Chrome executable." >&2
    exit 1
  fi
fi

cd "$REPO_ROOT/frontend"
node scripts/store-screenshots.mjs "$TARGET"
echo "Screenshots written under fastlane/metadata/ios/en-US/screenshots/ and store-meta/"
