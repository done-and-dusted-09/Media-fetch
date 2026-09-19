package com.mediafetch.runtime
import com.arthenica.ffmpegkit.FFmpegKit
import com.chaquo.python.Python
/** Points yt-dlp at the bundled FFmpeg (FFmpegKit native lib, no system PATH use). */
object FfmpegManager {
  fun ffmpegDir(): String = com.arthenica.ffmpegkit.FFmpegKitConfig.getSafParameter(null) ?: ""
  fun version(): String = try { FFmpegKit.getVersion() } catch (e: Exception) { "unknown: $e" }
}
/** Bundled QuickJS binary (NDK-built qjs in jniLibs). yt-dlp --js-runtimes quickjs:<path>. */
object JsRuntimeManager {
  @Volatile var qjsPath: String = ""
  fun configuredArgs(): String = if (qjsPath.isEmpty()) "" else "quickjs:$qjsPath"
}
data class Health(val name: String, val ok: Boolean, val version: String, val detail: String)
/** Offline startup health check: imports + binary probes, zero network. */
object ComponentHealth {
  fun check(ffmpegPath: String, ffprobePath: String, qjsPath: String): List<Health> {
    val out = mutableListOf<Health>()
    try {
      val v = Python.getInstance().getModule("health_update").callAttr("yt_dlp_version").toString()
      out += Health("Bundled Python", true, "CPython via Chaquopy", "interpreter OK")
      out += Health("yt-dlp", true, v, "bundled, deterministic until user updates")
    } catch (e: Exception) { out += Health("yt-dlp", false, "", "$e") }
    out += Health("FFmpeg", ffmpegPath.isNotEmpty(), FfmpegManager.version(), ffmpegPath)
    out += Health("FFprobe", java.io.File(ffprobePath).canExecute(), "via FFprobeKit", ffprobePath)
    out += Health("JS runtime (QuickJS)", java.io.File(qjsPath).canExecute(), "bundled qjs", qjsPath)
    return out
  }
}
