"""Shared models: pure-python mirror of the Kotlin models.

Used by ytdlp_service / format_parser / download_manager and unit-tested on
desktop. The Android app uses the equivalent Kotlin data classes; field names
are kept identical so behaviour can be compared 1:1.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class MediaFormat:
    format_id: str
    ext: str = ""
    resolution: str = ""
    width: Optional[int] = None
    height: Optional[int] = None
    fps: Optional[float] = None
    vcodec: str = "none"
    acodec: str = "none"
    tbr: Optional[float] = None
    filesize: Optional[int] = None
    filesize_approx: Optional[int] = None
    format_note: str = ""
    has_video: bool = False
    has_audio: bool = False
    url: str = ""

    @property
    def kind(self) -> str:
        if self.has_video and self.has_audio:
            return "combined"
        if self.has_video:
            return "video_only"
        if self.has_audio:
            return "audio_only"
        return "unknown"

    @property
    def effective_size(self) -> Optional[int]:
        return self.filesize if self.filesize is not None else self.filesize_approx

    def friendly_label(self) -> str:
        if self.kind == "audio_only":
            return f"Best Audio \u2022 {self.ext.upper() or 'AUDIO'}".strip()
        res = self.resolution or (f"{self.height}p" if self.height else "Unknown")
        fps = f" \u2022 {int(self.fps)} FPS" if self.fps else ""
        codec = (self.vcodec or "").upper()
        suffix = "Video + Audio" if self.kind == "combined" else "Video Only"
        parts = f"{res} \u2022 {(self.ext or '').upper()}".strip()
        if codec and codec != "NONE":
            parts += f" \u2022 {codec}"
        return f"{parts}{fps} \u2022 {suffix}"


@dataclass
class VideoInfo:
    title: str = ""
    uploader: str = ""
    duration: Optional[int] = None
    webpage_url: str = ""
    thumbnail: str = ""
    extractor: str = ""
    formats: list[MediaFormat] = field(default_factory=list)

    def grouped(self) -> dict[str, list[MediaFormat]]:
        groups: dict[str, list[MediaFormat]] = {
            "combined": [], "video_only": [], "audio_only": [],
        }
        for f in self.formats:
            groups.setdefault(f.kind, []).append(f)
        return groups


@dataclass
class ProgressEvent:
    status: str  # downloading | finished | error
    filename: str = ""
    downloaded_bytes: int = 0
    total_bytes: Optional[int] = None
    speed: Optional[float] = None
    eta: Optional[int] = None
    percent: Optional[float] = None

    @classmethod
    def from_hook(cls, d: dict[str, Any]) -> "ProgressEvent":
        total = d.get("total_bytes") or d.get("total_bytes_estimate")
        downloaded = int(d.get("downloaded_bytes") or 0)
        percent = (downloaded / total * 100.0) if total else None
        return cls(
            status=str(d.get("status", "")),
            filename=str(d.get("filename", "")),
            downloaded_bytes=downloaded,
            total_bytes=total,
            speed=d.get("speed"),
            eta=d.get("eta"),
            percent=percent,
        )
