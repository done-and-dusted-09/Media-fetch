package com.mediafetch.storage
import java.io.File
/** Scoped-storage-friendly store: MediaStore/Downloads on Android 10+, SAF picker for custom dir. */
class DownloadStore(private val defaultDir: File) {
  data class Entry(val title: String, val detail: String, val path: String, val date: String)
  private val history = mutableListOf<Entry>()
  fun defaultDir(): File = defaultDir.also { it.mkdirs() }
  fun record(e: Entry) { history.add(0, e) }
  fun history(): List<Entry> = history.toList()
}
