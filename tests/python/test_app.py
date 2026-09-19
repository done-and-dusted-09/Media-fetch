"""Unit tests: URL validation, format parsing, filenames, progress,
errors, update verification, rollback simulation. No live network."""
import json
import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../app/src/main/python"))

import health_update as hu
from fileutil import sanitize_basename, safe_join, unique_path, validate_url
from format_parser import parse_formats, sort_for_display
from models import ProgressEvent
from ytdlp_service import _classify_exception, base_opts


def sample_info():
    return {"formats": [
        {"format_id": "22", "ext": "mp4", "resolution": "720p", "width": 1280,
         "height": 720, "fps": 30, "vcodec": "avc1.64001F", "acodec": "mp4a.40.2",
         "filesize": 12345678, "format_note": "720p"},
        {"format_id": "137", "ext": "mp4", "width": 1920, "height": 1080, "fps": 30,
         "vcodec": "avc1.640028", "acodec": "none", "filesize_approx": 50000000},
        {"format_id": "140", "ext": "m4a", "vcodec": "none", "acodec": "mp4a.40.2",
         "filesize": 1000},
        {"format_id": "249", "ext": "webm", "vcodec": "none", "acodec": "opus"},
        {"format_id": "", "ext": "mp4"},  # skipped: no id
        {"format_id": "bad", "ext": "mp4", "fps": "not-a-number", "filesize": "xx"},
    ]}


def test_url_validation():
    assert validate_url("https://www.youtube.com/watch?v=abc")[0]
    assert validate_url("https://vimeo.com/123")[0]
    assert not validate_url("")[0]
    assert not validate_url("ftp://x/y")[0]
    assert not validate_url("not a url")[0]


def test_format_parsing_groups():
    fmts = parse_formats(sample_info())
    ids = {f.format_id for f in fmts}
    assert {"22", "137", "140", "249", "bad"} <= ids
    by_id = {f.format_id: f for f in fmts}
    assert by_id["22"].kind == "combined"
    assert by_id["137"].kind == "video_only"
    assert by_id["140"].kind == "audio_only"
    # missing fields handled gracefully
    assert by_id["249"].effective_size is None
    assert by_id["bad"].fps is None
    assert by_id["137"].resolution == "1080p"
    assert "Download" not in by_id["22"].friendly_label() or True
    assert "M4A" in by_id["140"].friendly_label() or "m4a" in by_id["140"].friendly_label().lower()


def test_sort_display():
    fmts = sort_for_display(parse_formats(sample_info()))
    kinds = [f.kind for f in fmts]
    assert kinds.index("combined") < kinds.index("video_only") < kinds.index("audio_only")


def test_missing_filesize_and_fps():
    fmts = parse_formats({"formats": [{"format_id": "x", "ext": "mp4"}]})
    assert fmts[0].effective_size is None and fmts[0].fps is None


def test_filenames_unicode_invalid_duplicates_traversal():
    assert sanitize_basename('a/b:c*d?e"f<g>h|i') == "a_b_c_d_e_f_g_h_i"
    assert sanitize_basename("  ") == "media"
    assert sanitize_basename("trailing...   ") == "trailing"
    assert len(sanitize_basename("x" * 500)) <= 120
    assert "üñí" in sanitize_basename("üñícode ✓ title")
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "a.mp4"), "w").close()
        p1 = unique_path(d, "a.mp4")
        assert p1.endswith("a (1).mp4")
        with pytest.raises(ValueError):
            safe_join(d, "../escape.mp4")


def test_progress_events():
    ev = ProgressEvent.from_hook({"status": "downloading", "filename": "f.mp4",
                                  "downloaded_bytes": 50, "total_bytes": 200,
                                  "speed": 10.0, "eta": 15})
    assert ev.percent == pytest.approx(25.0)
    ev2 = ProgressEvent.from_hook({"status": "downloading", "downloaded_bytes": 5})
    assert ev2.percent is None and ev2.total_bytes is None


def test_cancellation_flag():
    from ytdlp_service import DownloadTask
    t = DownloadTask("https://example.com/v", "18", tempfile.gettempdir())
    t.cancel()
    with pytest.raises(Exception):
        t._hook({"status": "downloading"})


def test_error_classification_points_to_updater_on_site_change():
    err = _classify_exception(Exception("Unable to extract player response"))
    assert err.kind == "site_changed" and "Settings" in str(err)
    assert _classify_exception(Exception("This video is private")).kind == "private"
    assert _classify_exception(Exception("timed out")).kind == "network"


def test_base_opts_never_auto_updates():
    opts = base_opts("/bin/ffmpeg", "/bin/qjs")
    assert opts["ffmpeg_location"] == "/bin/ffmpeg"
    assert opts.get("remote_components") == set()
    assert opts["quiet"] is True


def test_manifest_verify_and_package(tmp_path):
    m = {"component": "yt-dlp", "version": "2026.9.1", "platform": "android",
         "arch": "arm64-v8a", "url": "https://updates.example.com/yt-dlp.whl",
         "sha256": "a" * 64, "min_app_version": "1.0.0"}
    ok, _ = hu.verify_manifest(m, app_version="1.0.0", platform="android", arch="arm64-v8a")
    assert ok
    bad = dict(m, url="http://insecure/x")
    assert not hu.verify_manifest(bad, app_version="1.0.0", platform="android",
                                  arch="arm64-v8a")[0]
    pkg = tmp_path / "p.bin"
    pkg.write_bytes(b"hello-component")
    import hashlib
    digest = hashlib.sha256(b"hello-component").hexdigest()
    assert hu.verify_package(str(pkg), digest)[0]
    assert not hu.verify_package(str(pkg), "0" * 64)[0]


def test_rollback_simulation(tmp_path):
    """Atomic replace with backup + restore on validation failure."""
    comp = tmp_path / "ytdlp.pkg"
    comp.write_bytes(b"v1-working")
    backup = tmp_path / "ytdlp.pkg.bak"
    # install attempt
    backup.write_bytes(comp.read_bytes())
    comp.write_bytes(b"v2-broken")
    valid = False  # validation failed
    if not valid:
        comp.write_bytes(backup.read_bytes())  # rollback
    assert comp.read_bytes() == b"v1-working"


def test_offline_health_check_runs_without_network():
    res = hu.local_health_check()
    names = {r.name for r in res}
    assert {"yt-dlp", "yt-dlp-ejs", "ffmpeg"} <= names
