#!/usr/bin/env bash
# Build CareerFlow mobile artifacts locally.
#
# Usage:   scripts/build-mobile.sh [android|ios|all]
# Requires: Node 20, JDK 17, Android SDK (for android), Xcode (for ios).
#
# This script is a thin wrapper around the same commands CI runs.

set -euo pipefail

TARGET="${1:-all}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT/frontend"

echo "==> Installing JS deps"
npm ci

echo "==> Ensuring Capacitor is present"
if ! grep -q '@capacitor/core' package.json; then
  npm install --save-dev @capacitor/cli@^6
  npm install --save @capacitor/core@^6
fi

echo "==> Building web bundle"
npm run build:web

build_android() {
  echo "==> Android: ensuring platform"
  if [ ! -d android ]; then
    npm install --save @capacitor/android@^6
    npx cap add android
  fi
  npx cap sync android

  echo "==> Android: gradle bundleRelease"
  cd android
  ./gradlew bundleRelease || ./gradlew bundleDebug
  cd ..
  echo "AAB(s):"
  find android/app/build/outputs/bundle -name '*.aab' -print
}

build_ios() {
  if [ "$(uname)" != "Darwin" ]; then
    echo "iOS builds require macOS — skipping." >&2
    return 0
  fi
  echo "==> iOS: ensuring platform"
  if [ ! -d ios ]; then
    npm install --save @capacitor/ios@^6
    npx cap add ios
  fi
  npx cap sync ios

  echo "==> iOS: archive (unsigned unless Fastlane secrets are exported)"
  cd "$REPO_ROOT/fastlane/ios"
  if command -v bundle >/dev/null 2>&1 && [ -n "${MATCH_PASSWORD:-}" ]; then
    bundle install
    bundle exec fastlane build
  else
    cd "$REPO_ROOT/frontend/ios/App"
    xcodebuild \
      -workspace App.xcworkspace \
      -scheme App \
      -configuration Release \
      -archivePath "$REPO_ROOT/build/CareerFlow.xcarchive" \
      CODE_SIGNING_ALLOWED=NO \
      archive
  fi
}

case "$TARGET" in
  android) build_android ;;
  ios)     build_ios ;;
  all)     build_android; build_ios ;;
  *)       echo "Unknown target: $TARGET (expected android|ios|all)" >&2; exit 2 ;;
esac

echo "Done."
