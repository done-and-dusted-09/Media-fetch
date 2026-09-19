"""Build a signed update package: zip component + write manifest with SHA-256.
Usage: python tools/make_update_package.py <component_dir> <out.zip> <version>
Only maintainers run this. The app verifies sha256 + platform/arch + HTTPS.
"""
import hashlib, json, sys, zipfile
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""): h.update(c)
    return h.hexdigest()
if __name__ == "__main__":
    src, out, ver = sys.argv[1], sys.argv[2], sys.argv[3]
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        import os
        for root, _, files in os.walk(src):
            for fn in files:
                full = os.path.join(root, fn)
                z.write(full, os.path.relpath(full, src))
    print(json.dumps({"component": src, "version": ver, "sha256": sha256(out), "file": out}, indent=2))
