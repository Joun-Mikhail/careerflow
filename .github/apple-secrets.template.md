# GitHub Actions secrets for iOS App Store publishing

Add these under **Repository → Settings → Secrets and variables → Actions → New repository secret**.

| Secret | Example / notes |
| --- | --- |
| `APPLE_TEAM_ID` | 10-character Team ID from [developer.apple.com/account](https://developer.apple.com/account) → Membership |
| `FASTLANE_USER` | Apple ID email used for App Store Connect |
| `FASTLANE_APPLE_APPLICATION_SPECIFIC_PASSWORD` | Generated at [appleid.apple.com](https://appleid.apple.com/account/manage) → App-Specific Passwords |
| `MATCH_PASSWORD` | Passphrase encrypting certs in your private match repo |
| `MATCH_GIT_URL` | SSH or HTTPS URL of a **private** git repo for signing certs (e.g. `git@github.com:you/careerflow-ios-certs.git`) |

## One-time local setup

```bash
# 1. Create App Store Connect app record
export FASTLANE_USER="you@example.com"
export APPLE_TEAM_ID="XXXXXXXXXX"
scripts/setup-apple-appstore.sh

# 2. Initialize signing (after creating a private certs repo)
export MATCH_GIT_URL="git@github.com:you/careerflow-ios-certs.git"
export MATCH_PASSWORD="your-passphrase"
export FASTLANE_APPLE_APPLICATION_SPECIFIC_PASSWORD="xxxx-xxxx-xxxx-xxxx"
scripts/setup-ios-signing.sh
```

## Verify CI signing

Trigger the **mobile-build** workflow manually. With secrets set, the iOS job produces a signed `CareerFlow.ipa` artifact.

## Publish to TestFlight

On a Mac with Xcode:

```bash
export FASTLANE_USER="..." FASTLANE_APPLE_APPLICATION_SPECIFIC_PASSWORD="..."
export APPLE_TEAM_ID="..." MATCH_PASSWORD="..." MATCH_GIT_URL="..."
scripts/publish-ios.sh beta
```

Or run `scripts/publish-ios.sh release` to upload metadata without submitting for review.
