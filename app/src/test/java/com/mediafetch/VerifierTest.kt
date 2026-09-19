package com.mediafetch
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
class VerifierTest {
  @Test fun rejectsHttpAndBadHash() {
    val m = JSONObject("""{"component":"yt-dlp","version":"1","platform":"android","arch":"arm64-v8a","url":"http://x/y","sha256":"00","min_app_version":"1.0.0"}""")
    val r = com.mediafetch.updater.ManifestVerifier.verify(m, "1.0.0", "android", "arm64-v8a")
    assert(!r.first)
  }
  @Test fun acceptsGoodManifest() {
    val m = JSONObject("""{"component":"yt-dlp","version":"2026.9.1","platform":"android","arch":"arm64-v8a","url":"https://u.example.com/p.whl","sha256":"${"a".repeat(64)}","min_app_version":"1.0.0"}""")
    assert(com.mediafetch.updater.ManifestVerifier.verify(m, "1.0.0", "android", "arm64-v8a").first)
  }
}
