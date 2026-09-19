"""Dynamic format parsing: info['formats'] -> list[MediaFormat].

Never hard-codes format IDs. Handles missing filesize/fps/codecs gracefully.
"""
from __future__ import annotations

from typing import Any, Optional

from models import MediaFormat


def _norm_codec(value: Any) -> str:
    if not value:
        return "none"
    s = str(value).strip()
    return s if s and s.lower() != "none" else "none"


def parse_format(raw: dict[str, Any]) -> Optional[MediaFormat]:
    if not isinstance(raw, dict):
        return None
    fid = str(raw.get("format_id", "") or "").strip()
    if not fid:
        return None
    vcodec = _norm_codec(raw.get("vcodec"))
    acodec = _norm_codec(raw.get("acodec"))
    has_video = vcodec != "none"
    has_audio = acodec != "none"
    width = raw.get("width")
    height = raw.get("height")
    try:
        width = int(width) if width is not None else None
        height = int(height) if height is not None else None
    except (TypeError, ValueError):
        width, height = None, None
    fps = raw.get("fps")
    try:
        fps = float(fps) if fps is not None else None
    except (TypeError, ValueError):
        fps = None
    resolution = str(raw.get("resolution") or "").strip()
    if resolution in ("", "audio only"):
        resolution = f"{height}p" if height else ("audio only" if has_audio and not has_video else "")
    for key in ("filesize", "filesize_approx", "tbr"):
        v = raw.get(key)
        try:
            raw[key] = None if v is None else (int(v) if key != "tbr" else float(v))
        except (TypeError, ValueError):
            raw[key] = None
    return MediaFormat(
        format_id=fid,
        ext=str(raw.get("ext") or ""),
        resolution=resolution,
        width=width,
        height=height,
        fps=fps,
        vcodec=vcodec,
        acodec=acodec,
        tbr=raw.get("tbr"),
        filesize=raw.get("filesize"),
        filesize_approx=raw.get("filesize_approx"),
        format_note=str(raw.get("format_note") or ""),
        has_video=has_video,
        has_audio=has_audio,
        url=str(raw.get("url") or ""),
    )


def parse_formats(info: dict[str, Any]) -> list[MediaFormat]:
    raw_list = (info or {}).get("formats") or []
    out: list[MediaFormat] = []
    for raw in raw_list:
        f = parse_format(raw)
        if f is not None:
            out.append(f)
    return out


def sort_for_display(formats: list[MediaFormat]) -> list[MediaFormat]:
    """Combined first (tallest first), then video-only, then audio-only."""
    rank = {"combined": 0, "video_only": 1, "audio_only": 2, "unknown": 3}

    def key(f: MediaFormat):
        return (rank.get(f.kind, 3), -(f.height or 0), -(f.tbr or 0.0), f.format_id)

    return sorted(formats, key=key)
