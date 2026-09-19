"""yt-dlp integration layer (runs under Chaquopy on Android, CPython on desktop).

Uses the official yt-dlp Python API only. No custom scrapers, no hard-coded
format IDs. Metadata extraction never downloads media (download=False).

On Android this module is loaded via Chaquopy's Python.getInstance(); paths
for ffmpeg / JS runtime / ejs are injected by Kotlin (see FfmpegManager and
JsRuntimeManager). The desktop/test path passes explicit overrides.
"""
from __future__ import annotations

import os
import threading
from typing import Any, Callable, Optional

import yt_dlp

from fileutil import sanitize_basename, validate_url
from format_parser import parse_formats
from models import ProgressEvent, VideoInfo

PINNED_YT_DLP = "2026.8.19"


class ExtractionError(Exception):
    """User-safe error with machine-readable kind + technical detail."""

    def __init__(self, kind: str, message: str, detail: str = ""):
        super().__init__(message)
        self.kind = kind
        self.detail = detail


def _classify_exception(exc: Exception) -> ExtractionError:
    msg = str(exc)
    low = msg.lower()
    if "private" in low:
        return ExtractionError("private", "This media appears to be private.", msg)
    if "login" in low or "sign in" in low or "cookies" in low or "auth" in low:
        return ExtractionError("auth_required",
                               "This content requires sign-in and cannot be downloaded.", msg)
    if "geo" in low or "country" in low or "region" in low or "blocked" in low:
        return ExtractionError("geo_blocked",
                               "This content is not available in your region.", msg)
    if "unsupported url" in low or "no video formats" in low and "url" in low:
        return ExtractionError("unsupported", "This URL is not supported.", msg)
    if "name or service not known" in low or "network" in low or "timed out" in low \
            or "connection" in low or "urlopen" in low:
        return ExtractionError("network", "Network error. Check your connection and retry.", msg)
    if "requested format not available" in low or "format" in low and "not available" in low:
        return ExtractionError("format_unavailable",
                               "The selected format is no longer available. Fetch formats again.", msg)
    if "ffmpeg" in low or "merger" in low or "postprocess" in low:
        return ExtractionError("ffmpeg", "Media processing (FFmpeg) failed.", msg)
    # Website changed and bundled yt-dlp can't cope -> point at updater.
    if "unable to extract" in low or "extractor" in low or "js challenge" in low \
            or "signature" in low or "player" in low:
        return ExtractionError(
            "site_changed",
            "This URL could not be processed by the currently installed downloader "
            "components.\nCheck for a downloader component update in Settings \u2192 Updates.",
            msg)
    return ExtractionError("extraction_failed",
                           "Unable to retrieve this video's formats.", msg)


def base_opts(ffmpeg_path: Optional[str] = None,
              js_runtime_path: Optional[str] = None,
              no_remote_components: bool = True) -> dict[str, Any]:
    """Common yt-dlp options. Never enables auto-update or remote downloads."""
    opts: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "no_color": True,
        "ignoreerrors": False,
        "noplaylist": True,
        "socket_timeout": 30,
        "retries": 3,
        # Critical: forbid yt-dlp fetching remote EJS components at runtime.
        # EJS scripts are bundled (yt-dlp[default]); updates come only via
        # the explicit Settings -> Updates flow.
        "remote_components": set(),
    }
    if ffmpeg_path:
        opts["ffmpeg_location"] = ffmpeg_path
    if js_runtime_path:
        # Bundled QuickJS binary, e.g. quickjs:/data/.../libqjs.so dir + qjs bin.
        opts["js_runtimes"] = {"quickjs": {"path": js_runtime_path}}
    return opts


def fetch_info(url: str,
               ffmpeg_path: Optional[str] = None,
               js_runtime_path: Optional[str] = None) -> VideoInfo:
    ok, reason = validate_url(url)
    if not ok:
        raise ExtractionError("invalid_url", f"That URL looks invalid. {reason}", url)
    opts = base_opts(ffmpeg_path, js_runtime_path)
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except ExtractionError:
        raise
    except Exception as exc:  # noqa: BLE001 - classified below
        raise _classify_exception(exc) from exc
    if not info:
        raise ExtractionError("extraction_failed", "Unable to retrieve this video's formats.", "")
    if info.get("_type") == "playlist":
        entries = info.get("entries") or []
        info = entries[0] if entries else info
    formats = parse_formats(info)
    thumb = info.get("thumbnail") or ""
    if not thumb:
        thumbs = info.get("thumbnails") or []
        if thumbs:
            thumb = thumbs[-1].get("url") or ""
    return VideoInfo(
        title=str(info.get("title") or "Unknown title"),
        uploader=str(info.get("uploader") or info.get("channel") or ""),
        duration=info.get("duration"),
        webpage_url=str(info.get("webpage_url") or url),
        thumbnail=thumb,
        extractor=str(info.get("extractor") or ""),
        formats=formats,
    )


class DownloadCancelled(Exception):
    pass


class DownloadTask:
    """One active download. Cancellation via flag checked in progress hook."""

    def __init__(self, url: str, format_id: str, out_dir: str,
                 ffmpeg_path: Optional[str] = None,
                 js_runtime_path: Optional[str] = None,
                 on_progress: Optional[Callable[[ProgressEvent], None]] = None):
        self.url = url
        self.format_id = format_id
        self.out_dir = out_dir
        self.ffmpeg_path = ffmpeg_path
        self.js_runtime_path = js_runtime_path
        self.on_progress = on_progress
        self._cancel = threading.Event()
        self.result_path: Optional[str] = None

    def cancel(self) -> None:
        self._cancel.set()

    def _hook(self, d: dict[str, Any]) -> None:
        if self._cancel.is_set():
            raise DownloadCancelled("Download cancelled by user.")
        if self.on_progress:
            ev = ProgressEvent.from_hook(d)
            self.on_progress(ev)
        if d.get("status") == "finished":
            self.result_path = d.get("filename")

    def run(self) -> str:
        ok, reason = validate_url(self.url)
        if not ok:
            raise ExtractionError("invalid_url", f"That URL looks invalid. {reason}", self.url)
        os.makedirs(self.out_dir, exist_ok=True)
        template = os.path.join(self.out_dir, "%(title).120B [%(id)s].%(ext)s")
        opts = base_opts(self.ffmpeg_path, self.js_runtime_path)
        opts.update({
            "format": self.format_id,  # exact ID user picked; yt-dlp merges via FFmpeg if needed
            "outtmpl": template,
            "restrictfilenames": True,
            "windowsfilenames": True,
            "progress_hooks": [self._hook],
            "merge_output_format": None,  # keep source container; yt-dlp + FFmpeg merge
            "postprocessors": [{"key": "FFmpegMetadata", "add_metadata": True}],
            "continuedl": True,
        })
        # Pre-resolve a safe display name (actual file comes from yt-dlp template).
        _ = sanitize_basename(self.format_id)
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([self.url])
        except DownloadCancelled:
            raise
        except Exception as exc:  # noqa: BLE001
            if self._cancel.is_set():
                raise DownloadCancelled("Download cancelled by user.") from exc
            raise _classify_exception(exc) from exc
        if not self.result_path:
            raise ExtractionError("download_failed", "Download finished but no file was produced.", "")
        return self.result_path
