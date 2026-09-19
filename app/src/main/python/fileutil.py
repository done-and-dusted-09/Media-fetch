"""Filename + URL utilities. No network, no yt-dlp import: unit-testable."""
from __future__ import annotations

import os
import re
from urllib.parse import urlparse

_INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_TRAILING = re.compile(r'[.\s]+$')
MAX_BASENAME = 120


def validate_url(url: str) -> tuple[bool, str]:
    """Return (ok, reason). Accepts any http(s) URL yt-dlp could handle.

    We deliberately do NOT whitelist only YouTube: yt-dlp supports ~1000
    sites, so the check is syntactic. Unsupported hosts fail later at
    extraction with a user-friendly error.
    """
    if not url or not url.strip():
        return False, "URL is empty."
    url = url.strip()
    try:
        parts = urlparse(url)
    except Exception:
        return False, "URL could not be parsed."
    if parts.scheme not in ("http", "https"):
        return False, "URL must start with http:// or https://."
    if not parts.netloc or "." not in parts.netloc:
        return False, "URL host looks invalid."
    if len(url) > 2048:
        return False, "URL is too long."
    return True, ""


def sanitize_basename(name: str, fallback: str = "media") -> str:
    """Strip invalid chars, control chars, trailing dots/spaces; cap length."""
    name = (name or "").strip()
    if not name:
        return fallback
    name = _INVALID_CHARS.sub("_", name)
    name = _TRAILING.sub("", name).strip()
    if not name:
        return fallback
    if len(name) > MAX_BASENAME:
        name = name[:MAX_BASENAME].rstrip(" .")
    return name or fallback


def safe_join(directory: str, filename: str) -> str:
    """Join and guarantee the result stays inside directory (no traversal)."""
    base = os.path.abspath(directory)
    target = os.path.abspath(os.path.join(base, filename))
    if target != base and not target.startswith(base + os.sep):
        raise ValueError("Filename would escape the download directory.")
    return target


def unique_path(directory: str, filename: str) -> str:
    """Append (1), (2), ... if the file already exists. Case-preserving."""
    candidate = safe_join(directory, filename)
    if not os.path.exists(candidate):
        return candidate
    stem, ext = os.path.splitext(filename)
    i = 1
    while True:
        alt = safe_join(directory, f"{stem} ({i}){ext}")
        if not os.path.exists(alt):
            return alt
        i += 1
