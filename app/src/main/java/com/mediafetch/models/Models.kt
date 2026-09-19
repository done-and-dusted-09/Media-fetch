package com.mediafetch.models
data class MediaFormat(val formatId: String, val ext: String = "", val resolution: String = "",
  val width: Int? = null, val height: Int? = null, val fps: Double? = null,
  val vcodec: String = "none", val acodec: String = "none", val tbr: Double? = null,
  val filesize: Long? = null, val filesizeApprox: Long? = null, val formatNote: String = "",
  val hasVideo: Boolean = false, val hasAudio: Boolean = false) {
  val kind: String get() = when { hasVideo && hasAudio -> "combined"
    hasVideo -> "video_only"; hasAudio -> "audio_only"; else -> "unknown" }
  fun friendlyLabel(): String {
    if (kind == "audio_only") return "Best Audio \u2022 ${(ext.ifEmpty { "audio" }).uppercase()}"
    val res = resolution.ifEmpty { height?.let { "${it}p" } ?: "Unknown" }
    val fpsS = fps?.let { " \u2022 ${it.toInt()} FPS" } ?: ""
    val codec = vcodec.uppercase().takeIf { it != "NONE" }?.let { " \u2022 $it" } ?: ""
    val suffix = if (kind == "combined") "Video + Audio" else "Video Only"
    return "$res \u2022 ${ext.uppercase()}$codec$fpsS \u2022 $suffix" }
}
data class VideoInfo(val title: String, val uploader: String, val duration: Long?,
  val webpageUrl: String, val thumbnail: String, val extractor: String, val formats: List<MediaFormat>)
data class DownloadState(val status: String, val filename: String = "", val percent: Double? = null,
  val downloadedBytes: Long = 0, val totalBytes: Long? = null, val speed: Double? = null,
  val eta: Long? = null)
data class UpdateInfo(val component: String, val currentVersion: String, val newVersion: String,
  val url: String, val sha256: String, val releaseNotes: String)
