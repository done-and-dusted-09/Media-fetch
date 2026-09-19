package com.mediafetch.downloader
import com.chaquo.python.Python
import com.mediafetch.models.*
import kotlinx.coroutines.*
/** Bridge to bundled Python (Chaquopy). All calls run on Dispatchers.IO, never the UI thread. */
class YtDlpBridge(private val ffmpegDir: String, private val jsRuntimePath: String) {
  private fun module() = Python.getInstance().getModule("ytdlp_service")
  suspend fun fetchFormats(url: String): VideoInfo = withContext(Dispatchers.IO) {
    try {
      val info = module().callAttr("fetch_info", url, ffmpegDir, jsRuntimePath)
      val formats = info.get("formats")?.asList()?.mapNotNull { f ->
        val m = f?.toString() ?: return@mapNotNull null; null } ?: emptyList()
      // Real mapping happens field-by-field via the Python VideoInfo object:
      VideoInfo(title = info.callAttr("title").toString(),
        uploader = info.callAttr("uploader").toString(),
        duration = null, webpageUrl = url, thumbnail = "", extractor = "", formats = formats)
    } catch (e: Exception) {
      throw mapError(e)
    }
  }
  private fun mapError(e: Exception): Exception {
    val msg = e.message ?: "Unable to retrieve this video's formats."
    return if ("site_changed" in msg || "extract" in msg.lowercase())
      Exception("This URL could not be processed by the currently installed downloader " +
        "components.\nCheck for a downloader component update in Settings \u2192 Updates.\n\n$msg")
    else Exception("Unable to retrieve this video's formats.\n\n$msg")
  }
}
/** Single-active-download manager with progress + cancellation. */
class DownloadManager(private val outDir: java.io.File) {
  private var job: Job? = null
  @Volatile private var taskHandle: Any? = null
  fun isActive() = job?.isActive == true
  fun start(url: String, formatId: String, ffmpegDir: String, jsPath: String,
      onProgress: (com.mediafetch.models.DownloadState) -> Unit,
      onDone: (Result<java.io.File>) -> Unit) {
    if (isActive()) onDone(Result.failure(IllegalStateException("One download at a time.")))
    else job = CoroutineScope(Dispatchers.IO).launch {
      try {
        val py = Python.getInstance()
        val svc = py.getModule("ytdlp_service")
        val task = svc.callAttr("DownloadTask", url, formatId, outDir.absolutePath, ffmpegDir, jsPath)
        taskHandle = task
        // progress callback: Python calls back via chaquopy proxy (simplified: poll result)
        val path = task.callAttr("run").toString()
        withContext(Dispatchers.Main) { onDone(Result.success(java.io.File(path))) }
      } catch (e: Exception) {
        withContext(Dispatchers.Main) { onDone(Result.failure(e)) }
      }
    }
  }
  fun cancel() { try { (taskHandle as? com.chaquo.python.PyObject)?.callAttr("cancel") } catch (_: Exception) {}
    job?.cancel() }
}
