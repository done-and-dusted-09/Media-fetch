"""Startup health check + update-package verification (pure python mirror).

Health check is fully offline: it imports bundled modules and probes for the
ffmpeg/ffprobe binaries + JS runtime + EJS data without any network call.
Update verification (SHA-256 + version/platform checks) mirrors the Kotlin
ManifestVerifier so it can be unit-tested on desktop.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass


@dataclass
class ComponentStatus:
    name: str
    ok: bool
    version: str = ""
    detail: str = ""


def yt_dlp_version() -> str:
    import yt_dlp

    return str(getattr(yt_dlp.version, "__version__", "unknown"))


def ejs_available() -> bool:
    try:
        import yt_dlp_ejs  # noqa: F401
        return True
    except Exception:
        return False


def exe_version(path: str, args: list[str]) -> str:
    import subprocess

    try:
        out = subprocess.run([path, *args], capture_output=True, text=True, timeout=10)
        text = (out.stdout or "") + "\n" + (out.stderr or "")
        return text.strip().splitlines()[0][:120] if text.strip() else ""
    except Exception as exc:
        return f"missing: {exc}"


def local_health_check(ffmpeg_path: str = "", ffprobe_path: str = "",
                       js_runtime_path: str = "") -> list[ComponentStatus]:
    """Offline health check. Never touches the network."""
    results: list[ComponentStatus] = []
    try:
        v = yt_dlp_version()
        results.append(ComponentStatus("yt-dlp", True, v, "bundled Python package"))
    except Exception as exc:  # noqa: BLE001
        results.append(ComponentStatus("yt-dlp", False, "", str(exc)))
    results.append(ComponentStatus("yt-dlp-ejs", ejs_available(),
                                   "bundled" if ejs_available() else "",
                                   "challenge-solver scripts" if ejs_available()
                                   else "MISSING: reinstall the app (never auto-download)."))
    for name, path, probe in (("ffmpeg", ffmpeg_path, ["-version"]),
                              ("ffprobe", ffprobe_path, ["-version"]),
                              ("js-runtime(quickjs)", js_runtime_path, ["--help"])):
        if path and os.path.isfile(path) and os.access(path, os.X_OK):
            results.append(ComponentStatus(name, True, exe_version(path, probe), path))
        elif not path:
            results.append(ComponentStatus(name, False, "", "path not configured"))
        else:
            results.append(ComponentStatus(name, False, "", f"not executable: {path}"))
    return results


# ---- update manifest verification (mirrors Kotlin ManifestVerifier) ----

REQUIRED_MANIFEST_FIELDS = ("component", "version", "platform", "arch",
                            "url", "sha256", "min_app_version")


def sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_manifest(manifest: dict, *, app_version: str,
                    platform: str, arch: str) -> tuple[bool, str]:
    for f in REQUIRED_MANIFEST_FIELDS:
        if f not in manifest or manifest[f] in ("", None):
            return False, f"Manifest missing field: {f}"
    if manifest["platform"] != platform:
        return False, f"Platform mismatch: {manifest['platform']} != {platform}"
    if manifest["arch"] not in (arch, "universal"):
        return False, f"Arch mismatch: {manifest['arch']} != {arch}"
    url = str(manifest["url"])
    if not url.startswith("https://"):
        return False, "Update URL must use HTTPS."
    sha = str(manifest["sha256"])
    if len(sha) != 64 or any(c not in "0123456789abcdefABCDEF" for c in sha):
        return False, "Manifest sha256 is malformed."
    return True, ""


def verify_package(path: str, expected_sha256: str) -> tuple[bool, str]:
    actual = sha256_of_file(path)
    if actual.lower() != expected_sha256.lower():
        return False, f"Checksum mismatch: expected {expected_sha256[:12]}\u2026 got {actual[:12]}\u2026"
    return True, actual


def load_manifest_file(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)
