# Publishing CareerFlow to the App Store and Google Play

This guide walks an operator through getting CareerFlow into both stores. The
repository already ships:

- A Capacitor wrapper ([`frontend/capacitor.config.json`](../frontend/capacitor.config.json))
- Fastlane lanes for both platforms ([`fastlane/`](../fastlane))
- Store metadata templates ([`store-meta/`](../store-meta), [`fastlane/metadata/`](../fastlane/metadata))
- A CI workflow that produces AAB and IPA artifacts ([`.github/workflows/mobile-build.yml`](../.github/workflows/mobile-build.yml))
- A privacy policy ([`docs/privacy-policy.md`](./privacy-policy.md))
- A trusted install landing page ([`landing/index.html`](../landing/index.html))

What it cannot ship for you: the legal entity, paid developer accounts, signing
certificates, and the act of submission. The steps below cover those.

---

## 1. Set up the developer accounts

| Store | Account | Cost | Time to approval |
| --- | --- | --- | --- |
| **App Store** | [Apple Developer Program](https://developer.apple.com/programs/enroll/) | $99 / year | 24–48 hours |
| **Google Play** | [Google Play Console](https://play.google.com/console/signup) | $25 one-time | A few hours to 2 days |

Once Apple approves your enrolment, note your **Team ID** (10 characters,
shown on the Membership page). For Google Play, finish identity verification
under **Setup → Account details**.

## 2. Generate signing material

### Android upload keystore

```bash
keytool -genkey -v -keystore upload.keystore \
  -alias careerflow -keyalg RSA -keysize 2048 -validity 9125
# encode for CI:
base64 -w 0 upload.keystore > upload.keystore.b64
```

Keep `upload.keystore` somewhere safe. The base64 blob goes into the GitHub
secret below.

### Google Play service account

In Play Console → **Setup → API access**:

1. Link a Google Cloud project.
2. Create a service account with role *Release Manager*.
3. Download the JSON key. The entire file contents become the
   `GOOGLE_PLAY_JSON_KEY` secret.

### Apple signing

Two options:

- **fastlane match** (recommended) — store certs in a private git repo,
  passphrase-encrypted. Run `fastlane match init` locally once.
- **Manual** — create a *Distribution* certificate and *App Store* provisioning
  profile via Apple Developer → Certificates, Identifiers & Profiles, then
  drop them into Xcode.

You also need an **app-specific password** for the Apple ID that owns
App Store Connect, generated at
[appleid.apple.com](https://appleid.apple.com/account/manage) →
*App-Specific Passwords*.

## 3. Add GitHub Actions secrets

Repository → **Settings → Secrets and variables → Actions → New repository
secret**:

| Secret | Purpose |
| --- | --- |
| `ANDROID_KEYSTORE_BASE64` | base64 of `upload.keystore` |
| `ANDROID_KEYSTORE_PASSWORD` | keystore password |
| `ANDROID_KEY_ALIAS` | `careerflow` (or your alias) |
| `ANDROID_KEY_PASSWORD` | key password |
| `GOOGLE_PLAY_JSON_KEY` | service-account JSON (entire file) |
| `APPLE_TEAM_ID` | 10-char Team ID |
| `FASTLANE_USER` | Apple ID email |
| `FASTLANE_APPLE_APPLICATION_SPECIFIC_PASSWORD` | app-specific password |
| `MATCH_PASSWORD` | passphrase used by `fastlane match` |
| `MATCH_GIT_URL` | private repo URL with signing certs |

Once these are set, push to `main` (or trigger the `mobile-build` workflow
manually). CI will produce a signed AAB and IPA as workflow artifacts.

## 4. Create the store listings

### Apple App Store Connect

1. [App Store Connect → My Apps → "+"](https://appstoreconnect.apple.com/apps).
2. Bundle ID: `com.careerflow.app`. SKU: `careerflow`.
3. Copy the metadata fields from [`fastlane/metadata/ios/en-US/`](../fastlane/metadata/ios/en-US/).
4. Upload screenshots into the **6.7"**, **6.5"**, and **5.5"** display slots.
   Generate them with `scripts/generate-screenshots.sh appstore`.
5. **App Privacy** — answer the data-collection questionnaire using the
   matrix in [`docs/privacy-policy.md`](./privacy-policy.md): we collect
   email + user content + crash data (if Sentry is on); none of it is used
   for tracking.
6. Submit via `bundle exec fastlane release` from [`fastlane/ios/`](../fastlane/ios/).
   The lane uses `deliver` to attach metadata, then uploads the build.

### Google Play Console

1. [Play Console → All apps → Create app](https://play.google.com/console).
2. Default language: English (US). App name: **CareerFlow — Job Search Tracker**.
3. Copy fields from [`fastlane/metadata/android/en-US/`](../fastlane/metadata/android/en-US/).
4. Upload the feature graphic and phone screenshots.
5. Complete the **Data safety** form using the privacy-policy matrix.
6. Promote a CI-built AAB into **Internal testing**, then **Production** with
   `bundle exec fastlane release` from [`fastlane/android/`](../fastlane/android/).

## 5. Point the install landing page at real store URLs

Edit [`landing/index.html`](../landing/index.html) — replace the placeholder
`APPSTORE_URL` and `PLAYSTORE_URL` constants near the bottom of the file with
the real listing URLs once they are live. Then redeploy the frontend.

## 6. Final checklist before submission

- [ ] Live API URL baked into the build (CI sets `VITE_API_BASE_URL`).
- [ ] App icon present at every required size — see
  [`frontend/public/native-assets/`](../frontend/public/native-assets/) and run
  `npx @capacitor/assets generate` to regenerate per-platform sizes.
- [ ] Privacy policy URL: `https://github.com/Joun-Mikhail/careerflow/blob/main/docs/privacy-policy.md`
- [ ] Support URL: `https://github.com/Joun-Mikhail/careerflow/issues`
- [ ] App Store Connect "Sign in info" filled with the seeded demo account
  (`demo@careerflow.app` / `DemoPass123!`) so reviewers can log in.
- [ ] Build runs on the production API; smoke-test register/login from the
  archive before submitting.

That is everything CareerFlow needs to ship to both stores.
