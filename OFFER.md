# Offer: iOS CI/CD Pipeline Installation — $499

One flat price. Async only — no calls, no meetings. One job at a time.

Sold by **Yassine Lamtalaa**. Reference implementation: this repository, running the pipeline on itself ([latest green deploy run](https://github.com/lamtalaa/CICDPipelinePOC/actions/runs/29436912438)).

## Scope — what you get

I open a pull request in **your** iOS repository containing this pipeline, adapted to your project:

- A GitHub Actions workflow that on every **pull request to `main`** runs SwiftLint, runs your unit tests on a simulator, enforces a configurable code coverage threshold, publishes a job summary, and posts one persistent quality report comment on the PR.
- On every **push to `main`** (after quality checks pass): installs your signing assets on the hosted macOS runner, builds and signs a release IPA with Fastlane, uploads it to TestFlight with generated “What to Test” release notes, and uploads the IPA and notes as workflow artifacts.
- Fastlane configuration (`Fastfile`, `Appfile`, `Gemfile`) adapted to your scheme, targets, and bundle identifier.
- SwiftLint configuration if you don't already have one.
- Optional Microsoft Teams notifications (Adaptive Card) if you provide a webhook URL.
- Written setup notes in the PR description: which secrets to add, how to configure the `qa-testflight` environment, and recommended branch protection.

Manual signing is used (your distribution certificate `.p12` + provisioning profile stored as GitHub secrets). This is not a Fastlane Match setup and does not require a separate certificates repo.

## Guarantee

**If a successful GitHub Actions deploy run does not upload a build to your TestFlight after you merge the PR and your secrets are valid, you do not pay.**

The guarantee covers exactly that: a green deploy run resulting in a build visible in TestFlight. It is **not** a guarantee of:

- App Store review approval (TestFlight or App Store).
- Fixing compile errors in your app. Your app must already build in Xcode.
- In-app purchase configuration or any App Store Connect product setup.

## What you must have

- An iOS app that **already builds in Xcode**.
- An **Apple Developer account** (paid membership) with the ability to create a distribution certificate, a provisioning profile, and an App Store Connect API key.
- A GitHub repository for the app. Private is fine — note that **GitHub bills you directly for macOS Actions minutes on private repos** (macOS minutes are metered at a 10x multiplier; public repos are free).

## Out of scope

- App Store release automation (this pipeline targets TestFlight).
- UI test automation (the pipeline intentionally runs unit tests only).
- Writing or fixing your app code or tests.
- Android, React Native, or Flutter pipelines.
- Ongoing maintenance or on-call support after delivery (I will answer reasonable follow-up questions about the delivered pipeline, async).
- Anything requiring a live call or screen share.

## Secrets checklist

You add these to **your repo** under **Settings → Secrets and variables → Actions**. I never see or handle your certificates or keys.

| Secret | What it is |
|---|---|
| `APP_IDENTIFIER` | Your app's bundle identifier, e.g. `com.yourco.yourapp` |
| `APPLE_TEAM_ID` | Your Apple Developer Team ID |
| `PROVISIONING_PROFILE_NAME` | The name of your App Store distribution provisioning profile |
| `BUILD_CERTIFICATE_BASE64` | Your Apple Distribution certificate `.p12`, base64-encoded |
| `P12_PASSWORD` | The password for the `.p12` file |
| `BUILD_PROVISION_PROFILE_BASE64` | The `.mobileprovision` file, base64-encoded |
| `KEYCHAIN_PASSWORD` | Any strong random string (used for the temporary CI keychain) |
| `ASC_KEY_ID` | App Store Connect API key ID |
| `ASC_ISSUER_ID` | App Store Connect API issuer ID |
| `ASC_KEY_CONTENT` | The App Store Connect API key `.p8` content, base64-encoded |
| `TEAMS_WEBHOOK_URL` | *Optional* — Microsoft Teams webhook for notifications |

Actions variable (optional): `COVERAGE_THRESHOLD` — minimum line coverage percentage; defaults to `70`.

The PR I open includes step-by-step instructions for generating and encoding each of these.

## How it works, start to finish

1. You reach out (GitHub issue on this repo, or through a listing — see [LISTING.md](LISTING.md)).
2. You invite me as a collaborator on your repo.
3. You add the secrets above to your repo.
4. I open a pull request with the pipeline adapted to your project. The PR itself will demonstrate the lint/test/coverage checks running.
5. You review and merge. The merge triggers the deploy job and a signed build lands in your TestFlight.
6. You confirm the build is in TestFlight and pay **$499** via PayPal: [paypal.me/ylamtalaa](https://paypal.me/ylamtalaa).

## Payment

- **$499 USD**, one-time, via PayPal: [paypal.me/ylamtalaa](https://paypal.me/ylamtalaa)
- Payment is due after the guarantee condition is met (successful deploy run with a build uploaded to your TestFlight).
- No deposits, no subscriptions, no upsells.
