#!/usr/bin/env bash
# One-time Apple App Store Connect setup for CareerFlow.
#
# Prerequisites (manual, ~1–2 days):
#   1. Enroll at https://developer.apple.com/programs/enroll/ ($99/yr)
#   2. Register App ID com.careerflow.app in Certificates, Identifiers & Profiles
#   3. Create an app-specific password at https://appleid.apple.com/account/manage
#
# Then export:
#   export FASTLANE_USER="you@example.com"
#   export FASTLANE_APPLE_APPLICATION_SPECIFIC_PASSWORD="xxxx-xxxx-xxxx-xxxx"
#   export APPLE_TEAM_ID="XXXXXXXXXX"
#
# Usage:
#   scripts/setup-apple-appstore.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

missing=()
[ -z "${FASTLANE_USER:-}" ] && missing+=("FASTLANE_USER")
[ -z "${APPLE_TEAM_ID:-}" ] && missing+=("APPLE_TEAM_ID")

if [ "${#missing[@]}" -gt 0 ]; then
  echo "Missing required environment variables: ${missing[*]}" >&2
  echo "" >&2
  echo "Before running this script:" >&2
  echo "  1. Enroll in the Apple Developer Program" >&2
  echo "  2. Note your Team ID from developer.apple.com → Membership" >&2
  echo "  3. Register bundle ID com.careerflow.app" >&2
  echo "  4. Export FASTLANE_USER and APPLE_TEAM_ID" >&2
  echo "" >&2
  echo "See docs/app-store-submission.md for the full checklist." >&2
  exit 1
fi

echo "==> Creating App Store Connect app record via fastlane produce"
cd "$REPO_ROOT/fastlane/ios"
gem install bundler --silent || true
bundle install
bundle exec fastlane setup_appstore

echo ""
echo "Done. Open App Store Connect → My Apps → CareerFlow to finish the listing."
echo "Next: scripts/setup-ios-signing.sh"
