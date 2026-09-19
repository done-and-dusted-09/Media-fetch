# MediaFetch — self-contained yt-dlp downloader for Android
Target: Android (minSdk 24, targetSdk 35, arm64-v8a + x86_64).
Embedded Python: **Chaquopy 16.x** (maintained Gradle plugin, Play-compliant,
bundled CPython, pip packages inside APK). Chosen over python-for-android/Kivy
(non-native UI, harder Play/scoped-storage story) and BeeWare (immature Android
media/FFmpeg story). Native Kotlin + Compose UI, Python only for yt-dlp logic.
| Component | Pinned | Bundled as |
|---|---|---|
| yt-dlp | 2026.8.19 (`yt-dlp[default]`) | Chaquopy pip install (APK) + `yt-dlp-ejs` scripts |
| JS runtime (REQUIRED since yt-dlp 2025.11.12 for full YouTube) | QuickJS | NDK-built `qjs` binary in jniLibs; `--js-runtimes quickjs:<path>`. Deno has no official Android builds; QuickJS is ~1MB, supported, needs no npm at runtime |
| FFmpeg/FFprobe | 8.1 (ffmpegkit-maintained `full:8.1.7`, LGPL) | Gradle AAR, SDK35 + 16KB-page aligned |
| Python | CPython 3.11 via Chaquopy | in-APK, never system python |
Zero runtime downloads: no pip/bootstrapper in app code. Only media traffic +
explicit Settings→Updates manifest/package fetch (HTTPS + SHA-256 + platform checks,
atomic install + backup/rollback).
## Build (maintainer machine with Android SDK)
1. Install Android Studio + SDK 35 + NDK r27.
2. Build the QuickJS `qjs` binaries per ABI (see docs/JS_RUNTIME.md) into `app/src/main/jniLibs/<abi>/libqjs.so` + `assets/qjs`.
3. `./gradlew :app:assembleRelease` (Chaquopy embeds Python + yt-dlp[default] at build time).
4. Sign with your keystore; publish AAB to Play.
## Test
- `python -m pytest tests/python -q` (12 unit tests, mocked yt-dlp, no network).
- `./gradlew :app:testDebugUnitTest` (JVM tests for verifier/installer).
- Integration (manual, needs network): `tests/integration/TEST_URLS.md` — fetch formats + one download + FFmpeg merge check.
- Clean-machine: install APK on emulator image without Python/ffmpeg; verify health screen all-green offline.
- Network audit: normal flow must show traffic only to target site (+ manifest host iff user pressed Check for Updates).
## Legal
Users must comply with copyright laws and site terms. No DRM circumvention; stock yt-dlp behavior only.
