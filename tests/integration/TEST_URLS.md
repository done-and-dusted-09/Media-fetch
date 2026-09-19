# Integration tests (manual — require network; never run as unit tests)
1. Fetch: pick any public video URL at test time (do NOT hard-code one into the app).
   Assert: `fetch_info` returns title + non-empty formats with video_only/audio_only present when site offers them.
2. Download: download the smallest audio-only format to a temp dir; assert file exists and >0 bytes.
3. Merge: download a video-only + audio-only pair via a combined format id (e.g. `bestvideo+bestaudio`-style
   selection is NOT used by the app; instead the exact user-picked id, or yt-dlp merge when the picked
   entry requires it); assert FFmpeg (bundled) produced a playable container.
4. Offline: airplane mode — app launches, About/health visible, fetch fails with friendly error.
