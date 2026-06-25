#!/usr/bin/env bash
# Initialize iOS code signing with fastlane match.
#
# One-time setup:
#   1. Create a PRIVATE git repo for signing material (e.g. careerflow-ios-certs)
#   2. Export:
#        export FASTLANE_USER="you@example.com"
#        export FASTLANE_APPLE_APPLICATION_SPECIFIC_PASSWORD="xxxx-xxxx-xxxx-xxxx"
#        export APPLE_TEAM_ID="XXXXXXXXXX"
#        export MATCH_GIT_URL="git@github.com:you/careerflow-ios-certs.git"
#        export MATCH_PASSWORD="a-strong-passphrase"
#   3. Run: scripts/setup-ios-signing.sh
#
# Then add the same values as GitHub Actions secrets (see .github/apple-secrets.template.md).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

missing=()
[ -z "${FASTLANE_USER:-}" ] && missing+=("FASTLANE_USER")
[ -z "${APPLE_TEAM_ID:-}" ] && missing+=("APPLE_TEAM_ID")
[ -z "${MATCH_GIT_URL:-}" ] && missing+=("MATCH_GIT_URL")
[ -z "${MATCH_PASSWORD:-}" ] && missing+=("MATCH_PASSWORD")

if [ "${#missing[@]}" -gt 0 ]; then
  echo "Missing required environment variables: ${missing[*]}" >&2
  echo "See .github/apple-secrets.template.md for details." >&2
  exit 1
fi

echo "==> Generating App Store distribution cert + profile via fastlane match"
cd "$REPO_ROOT/fastlane/ios"
gem install bundler --silent || true
bundle install
bundle exec fastlane setup_signing

echo ""
echo "Signing material stored in: $MATCH_GIT_URL"
echo "Add these GitHub Actions secrets for CI signing:"
echo "  APPLE_TEAM_ID, FASTLANE_USER, FASTLANE_APPLE_APPLICATION_SPECIFIC_PASSWORD,"
echo "  MATCH_PASSWORD, MATCH_GIT_URL"
