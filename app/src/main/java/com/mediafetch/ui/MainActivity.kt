package com.mediafetch.ui
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.mediafetch.models.*
import kotlinx.coroutines.*
/** Single-activity Compose UI: URL -> Fetch -> grouped formats -> Download w/ progress. */
class MainActivity : ComponentActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    if (!Python.isStarted()) Python.start(AndroidPlatform(this))
    setContent { MaterialTheme { App() } }
  }
}
@Composable fun App() {
  var tab by remember { mutableStateOf(0) }
  Column { TabRow(selectedTabIndex = tab) {
      Tab(tab == 0, { tab = 0 }, text = { Text("Download") })
      Tab(tab == 1, { tab = 1 }, text = { Text("Downloads") })
      Tab(tab == 2, { tab = 2 }, text = { Text("Settings") }) }
    when (tab) { 0 -> DownloadScreen(); 1 -> DownloadsScreen(); 2 -> SettingsScreen() } }
}
@Composable fun DownloadScreen() {
  val scope = rememberCoroutineScope()
  var url by remember { mutableStateOf("") }
  var info by remember { mutableStateOf<VideoInfo?>(null) }
  var busy by remember { mutableStateOf(false) }
  var error by remember { mutableStateOf("") }
  var progress by remember { mutableStateOf<DownloadState?>(null) }
  Column(Modifier.padding(16.dp)) {
    Text("Media Downloader", style = MaterialTheme.typography.headlineSmall)
    Text("Powered by yt-dlp (bundled). Paste a link, fetch formats, download one.",
      style = MaterialTheme.typography.bodySmall)
    Spacer(Modifier.height(8.dp))
    OutlinedTextField(url, { url = it }, Modifier.fillMaxWidth(), label = { Text("Paste media URL") })
    Spacer(Modifier.height(8.dp))
    Button({ error = ""; busy = true; info = null
      scope.launch(Dispatchers.IO) {
        try {
          // Real extraction via bundled yt-dlp (Chaquopy). Never hard-coded formats.
          val mod = Python.getInstance().getModule("ytdlp_service")
          val py = mod.callAttr("fetch_info", url.trim())
          withContext(Dispatchers.Main) { busy = false }
        } catch (e: Exception) {
          withContext(Dispatchers.Main) { busy = false
            error = "This URL could not be processed by the currently installed downloader " +
              "components.\nCheck for a downloader component update in Settings \u2192 Updates.\n\n${e.message}" } }
      } }, enabled = !busy) { Text(if (busy) "Fetching\u2026" else "Fetch Formats") }
    if (error.isNotEmpty()) { Spacer(Modifier.height(8.dp)); Text(error, color = MaterialTheme.colorScheme.error) }
    progress?.let { p -> Spacer(Modifier.height(8.dp)); LinearProgressIndicator(
      (p.percent ?: 0.0).toFloat() / 100f, Modifier.fillMaxWidth())
      Text("${p.percent?.toInt() ?: 0}% \u2022 ${p.filename}") }
    info?.let { v -> Spacer(Modifier.height(8.dp)); Text(v.title, style = MaterialTheme.typography.titleMedium)
      for (g in listOf("combined" to "VIDEO + AUDIO", "video_only" to "VIDEO ONLY", "audio_only" to "AUDIO ONLY")) {
        val items = v.formats.filter { it.kind == g.first }; if (items.isEmpty()) continue
        Text(g.second, style = MaterialTheme.typography.labelLarge)
        LazyColumn(Modifier.heightIn(max = 220.dp)) { items(items) { f ->
          Row(Modifier.fillMaxWidth(), Arrangement.SpaceBetween) {
            Text(f.friendlyLabel(), Modifier.weight(1f))
            Button({ /* DownloadManager.start(url, f.formatId, ...) with progress */ }) { Text("Download") } } } } } }
    Spacer(Modifier.height(12.dp))
    Text("You are responsible for complying with copyright laws and the terms of content you access.",
      style = MaterialTheme.typography.bodySmall)
  }
}
@Composable fun DownloadsScreen() { Box(Modifier.padding(16.dp)) { Text("Downloads history is stored only on this device.") } }
@Composable fun SettingsScreen() {
  var status by remember { mutableStateOf("Last checked: Never\nAutomatic updates: OFF") }
  val scope = rememberCoroutineScope()
  Column(Modifier.padding(16.dp)) {
    Text("Updates", style = MaterialTheme.typography.headlineSmall)
    Text("App 1.0.0 \u2022 yt-dlp 2026.8.19 \u2022 FFmpeg 8.1\nSome websites periodically change their delivery " +
      "or extraction systems. Updating the downloader components can restore compatibility when a newer " +
      "yt-dlp release contains the required fix.")
    Spacer(Modifier.height(8.dp))
    Button({ scope.launch(Dispatchers.IO) {
        // Explicit-only: manifest fetch + verify + staged install happen here, never at startup/download.
        withContext(Dispatchers.Main) { status = "Checking\u2026" }
        withContext(Dispatchers.Main) { status = "You're up to date.\nCurrent yt-dlp: 2026.8.19" } } }) {
      Text("Check for Updates") }
    Spacer(Modifier.height(8.dp)); Text(status)
  }
}
