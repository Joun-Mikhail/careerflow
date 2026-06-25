#!/usr/bin/env bash
# Build and publish CareerFlow to TestFlight or App Store Connect.
#
# Usage:
#   scripts/publish-ios.sh [beta|release|submit]
#
#   beta    — build signed IPA + upload to TestFlight (default)
#   release — upload metadata + binary (does not submit for review)
#   submit  — submit latest build for Apple review (metadata only)
#
# Requires macOS + Xcode + signing env vars (see .github/apple-secrets.template.md).

set -euo pipefail

LANE="${1:-beta}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [ "$(uname)" != "Darwin" ]; then
  echo "iOS publishing requires macOS with Xcode installed." >&2
  exit 1
fi

missing=()
[ -z "${FASTLANE_USER:-}" ] && missing+=("FASTLANE_USER")
[ -z "${APPLE_TEAM_ID:-}" ] && missing+=("APPLE_TEAM_ID")

if [ "$LANE" != "submit" ]; then
  [ -z "${MATCH_PASSWORD:-}" ] && missing+=("MATCH_PASSWORD")
  [ -z "${MATCH_GIT_URL:-}" ] && missing+=("MATCH_GIT_URL")
  [ -z "${FASTLANE_APPLE_APPLICATION_SPECIFIC_PASSWORD:-}" ] && missing+=("FASTLANE_APPLE_APPLICATION_SPECIFIC_PASSWORD")
fi

if [ "${#missing[@]}" -gt 0 ]; then
  echo "Missing required environment variables: ${missing[*]}" >&2
  echo "See .github/apple-secrets.template.md" >&2
  exit 1
fi

echo "==> Generating native assets"
cd "$REPO_ROOT/frontend"
if [ -f public/native-assets/icon.png ]; then
  npm install --save-dev @capacitor/cli@^6 @capacitor/assets@^3 2>/dev/null || true
  npx @capacitor/assets generate \
    --iconBackgroundColor "#4f46e5" \
    --splashBackgroundColor "#4f46e5" \
    --assetPath public/native-assets 2>/dev/null || echo "(capacitor assets skipped — run after cap add ios)"
fi

echo "==> Building web bundle"
npm ci
npm run build:web

echo "==> Syncing Capacitor iOS project"
npm install --save @capacitor/core@^6 @capacitor/ios@^6 2>/dev/null || true
npx cap add ios 2>/dev/null || true
npx cap sync ios

echo "==> Running fastlane $LANE"
cd "$REPO_ROOT/fastlane/ios"
gem install bundler --silent || true
bundle install
bundle exec fastlane "$LANE"

echo ""
case "$LANE" in
  beta)
    echo "Uploaded to TestFlight. Install via App Store Connect → TestFlight."
    ;;
  release)
    echo "Build + metadata uploaded. Submit for review in App Store Connect or run:"
    echo "  scripts/publish-ios.sh submit"
    ;;
  submit)
    echo "Submitted for Apple review. Typical review time: 1–7 days."
    echo "After approval, update store-urls.json with the real App Store URL and run:"
    echo "  node frontend/scripts/sync-store-urls.mjs"
    ;;
esac
