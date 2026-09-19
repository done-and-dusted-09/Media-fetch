# Why Chaquopy (decision record)
Requirement: polished native Android app, bundled Python + yt-dlp + deps, Play-compliant,
scoped storage, background downloads, explicit secure updater.
- **Chaquopy (chosen)**: maintained (2026 releases), standard Gradle plugin, Play-safe,
  CPython 3.8–3.13, pip wheels incl. `yt-dlp[default]`, Kotlin-first UI (Compose/Material3),
  straightforward MediaStore/SAF/WorkManager integration, small APK delta (ABIs filtered).
- python-for-android + Kivy/Buildozer: maintained (v2026.05.09) but Kivy draws its own
  non-native UI (fails "polished native" bar), SDL bootstrap complicates scoped storage/
  notifications/Play 16KB-page + SDK35 story, recipe maintenance for Rust/C extensions.
- BeeWare/Briefcase+Toga: native widgets goal but Android backend/FFmpeg story immature
  for this media workload in 2026; higher integration risk for yt-dlp + FFmpeg merge.
# JS runtime (yt-dlp EJS, mandatory since 2025.11.12)
YouTube needs an external JS runtime + `yt-dlp-ejs` scripts. Deno (recommended on
desktop, >=2.3.0) publishes **no official Android binaries**; Node-for-Android is heavy.
Decision: bundle **QuickJS** (`qjs`) built with the NDK per ABI + pre-bundle `yt-dlp-ejs`
via the `default` pip extra at BUILD time. yt-dlp is configured with
`--js-runtimes quickjs:<bundled-path>` and `remote_components=set()` so normal use
never downloads EJS scripts. Fresh EJS comes only inside signed update packages.
# FFmpeg
Original `com.arthenica:ffmpeg-kit` retired Jan 2025, binaries removed Apr 2025.
Use maintained drop-in **`dev.ffmpegkit-maintained:ffmpeg-kit-full:8.1.7`** (LGPL,
FFmpeg 8.1, SDK35, 16KB aligned, arm64-v8a). Non-GPL variant keeps app license clean.
# Network audit expectation
Normal fetch/download: traffic only to target site/CDN. No PyPI/deno/ffmpeg hosts.
Update flow only after explicit tap: manifest host over HTTPS, then package host.
