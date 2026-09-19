# Clean-machine + network audit (release gate)
1. Fresh emulator image (no Python/ffmpeg/node on PATH); `adb install app-release.apk`.
2. Offline launch: app opens, Settings/About/health visible; yt-dlp 2026.8.19 + FFmpeg 8.1 + QuickJS shown green.
3. Online: paste URL -> Fetch Formats lists grouped formats; download one format; cancel works; file plays.
4. `adb shell` + proxy capture: confirm hosts are only target site/CDN during (3).
5. Updates: tap Check for Updates with bad sha package -> "could not be verified", install untouched; interrupt mid-install -> rollback restores.
