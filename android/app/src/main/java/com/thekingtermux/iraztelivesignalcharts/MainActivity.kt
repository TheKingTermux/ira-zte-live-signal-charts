package com.thekingtermux.iraztelivesignalcharts

import android.annotation.SuppressLint
import android.app.Activity
import android.graphics.Color
import android.graphics.drawable.ColorDrawable
import android.content.Intent
import android.content.ClipData
import android.content.ContentValues
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.provider.MediaStore
import android.provider.Settings
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.RenderProcessGoneDetail
import android.webkit.WebViewClient
import androidx.core.content.FileProvider
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.io.RandomAccessFile
import java.net.HttpURLConnection
import java.net.URL
import java.nio.ByteBuffer
import java.nio.channels.FileChannel
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference

class MainActivity : Activity() {
    private lateinit var webView: WebView
    private val repository = "TheKingTermux/ira-zte-live-signal-charts"

    // True bila proses renderer WebView dimatikan sistem; saat itu WebView lama tak bisa dipakai lagi.
    private var rendererGone = false

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Latar gelap sejak awal agar tidak ada kilatan putih sebelum splash screen tampil.
        window.setBackgroundDrawable(ColorDrawable(Color.parseColor("#020617")))
        webView = WebView(this)
        webView.setBackgroundColor(Color.parseColor("#020617"))
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.webChromeClient = WebChromeClient()
        webView.webViewClient = object : WebViewClient() {
            // Renderer dimatikan sistem (mis. memori rendah saat aplikasi di latar belakang): buat ulang
            // WebView dengan mulus. Tanpa penanganan ini aplikasi ikut crash dan dibuka dari awal.
            override fun onRenderProcessGone(view: WebView?, detail: RenderProcessGoneDetail?): Boolean {
                rendererGone = true
                runOnUiThread { recreate() }
                return true
            }
        }
        webView.addJavascriptInterface(RouterBridge(), "AndroidBridge")
        setContentView(webView)
        // Muat halaman hanya bila belum ada state yang bisa dipulihkan (mis. setelah proses dibunuh sistem).
        if (savedInstanceState == null || webView.restoreState(savedInstanceState) == null) {
            webView.loadUrl("file:///android_asset/index.html")
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        if (!rendererGone) webView.saveState(outState)
    }

    // launchMode singleTask: membuka aplikasi dari ikon/aplikasi lain hanya membawa Activity ke depan.
    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
    }

    override fun onResume() {
        super.onResume()
        webView.onResume()
        // Segarkan data langsung saat kembali dari aplikasi lain, tanpa memuat ulang halaman.
        webView.evaluateJavascript("window.onAppResume && window.onAppResume();", null)
    }

    override fun onPause() {
        webView.onPause()
        super.onPause()
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }

    private fun status(message: String, hasUpdate: Boolean = false) {
        val quoted = JSONObject.quote(message)
        val addButton = if (hasUpdate) """
            const btn = document.createElement('button');
            btn.id = 'apk-install-btn';
            btn.className = 'w-full bg-cyan-600 text-white text-xs px-3 py-2 rounded-xl';
            btn.textContent = 'Unduh & Pasang APK';
            btn.onclick = function() {
              document.getElementById('apk-update-status').textContent = 'Mengunduh APK...';
              AndroidBridge.downloadAndInstallApk(document.getElementById('apk-release-channel')?.value || 'stable');
            };
            section.appendChild(btn);
        """.trimIndent() else ""
        val script = """
            (function() {
              const section = document.getElementById('android-apk-updater');
              const status = document.getElementById('apk-update-status');
              if (status) status.textContent = $quoted;
              const old = document.getElementById('apk-install-btn');
              if (old) old.remove();
              if (section) { $addButton }
            })();
        """.trimIndent()
        runOnUiThread { webView.evaluateJavascript(script, null) }
    }

    // Hasil pemeriksaan update dikirim ke halaman (window.onApkUpdateResult di index.html).
    private fun updateResultToJs(result: JSONObject) {
        val script = "window.onApkUpdateResult && window.onApkUpdateResult($result);"
        runOnUiThread { webView.evaluateJavascript(script, null) }
    }

    // Progres unduhan untuk modal update (window.onApkDownloadProgress di index.html).
    private fun progress(percent: Double, downloaded: Long, total: Long, speed: Long, eta: Long) {
        val json = JSONObject().apply {
            put("percent", percent)
            put("downloaded", downloaded)
            put("total", total)
            put("speed", speed)
            put("eta", eta)
        }
        val script = "window.onApkDownloadProgress && window.onApkDownloadProgress($json);"
        runOnUiThread { webView.evaluateJavascript(script, null) }
    }

    // Hasil akhir unduhan/pemasangan untuk modal update (window.onApkDownloadDone di index.html).
    private fun downloadDone(ok: Boolean, message: String) {
        val script = "window.onApkDownloadDone && window.onApkDownloadDone($ok, ${JSONObject.quote(message)});"
        runOnUiThread { webView.evaluateJavascript(script, null) }
    }

    // Mengabarkan hasil ekspor ke halaman (window.onDiagnosticExport di index.html).
    private fun exportResult(ok: Boolean, message: String) {
        val script = "window.onDiagnosticExport && window.onDiagnosticExport($ok, ${JSONObject.quote(message)});"
        runOnUiThread { webView.evaluateJavascript(script, null) }
    }

    // Menyimpan salinan log ke Download/IRA ZTE. Android 10+ tidak butuh izin tambahan;
    // di versi lebih lama mengembalikan null (log tetap bisa dibagikan lewat share sheet).
    @SuppressLint("NewApi")
    private fun saveToDownloads(fileName: String, content: String): String? {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) return null
        return try {
            val values = ContentValues().apply {
                put(MediaStore.Downloads.DISPLAY_NAME, fileName)
                put(MediaStore.Downloads.MIME_TYPE, "application/json")
                put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/IRA ZTE")
                put(MediaStore.Downloads.IS_PENDING, 1)
            }
            val resolver = contentResolver
            val uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values) ?: return null
            try {
                val stream = resolver.openOutputStream(uri) ?: error("Tidak bisa membuka file tujuan")
                stream.use { it.write(content.toByteArray(Charsets.UTF_8)) }
                values.clear()
                values.put(MediaStore.Downloads.IS_PENDING, 0)
                resolver.update(uri, values, null, null)
            } catch (e: Exception) {
                resolver.delete(uri, null, null)
                return null
            }
            "Download/IRA ZTE/$fileName"
        } catch (e: Exception) {
            null
        }
    }

    private data class ApkRelease(
        val version: String,
        val url: String,
        val name: String = "",
        val body: String = "",
        val publishedAt: String = "",
        val htmlUrl: String = "",
        val size: Long = 0L
    )

    // JSONObject.optString mengembalikan teks "null" untuk nilai JSON null, jadi ditangani terpisah.
    private fun JSONObject.stringOrEmpty(key: String): String = if (isNull(key)) "" else optString(key, "")

    private fun latestApk(channel: String): ApkRelease {
        val normalizedChannel = if (channel.equals("beta", true)) "beta" else "stable"
        val endpoint = if (normalizedChannel == "stable") {
            "https://api.github.com/repos/$repository/releases/latest"
        } else {
            "https://api.github.com/repos/$repository/releases?per_page=30"
        }
        val conn = (URL(endpoint).openConnection() as HttpURLConnection).apply {
            connectTimeout = 10000
            readTimeout = 15000
            setRequestProperty("Accept", "application/vnd.github+json")
            setRequestProperty("User-Agent", "IRA-ZTE-Live-Signal-Charts-Android")
        }
        try {
            if (conn.responseCode !in 200..299) error("GitHub API HTTP ${conn.responseCode}")
            val body = conn.inputStream.bufferedReader().use { it.readText() }
            val releases = if (normalizedChannel == "stable") listOf(JSONObject(body)) else {
                val array = JSONArray(body)
                (0 until array.length()).mapNotNull { array.optJSONObject(it) }
                    .filterNot { it.optBoolean("draft") }
            }
            for (release in releases) {
                if (release.optBoolean("draft")) continue
                if (normalizedChannel == "stable" && release.optBoolean("prerelease")) continue
                val assets = release.optJSONArray("assets") ?: JSONArray()
                for (i in 0 until assets.length()) {
                    val asset = assets.optJSONObject(i) ?: continue
                    val name = asset.optString("name")
                    val url = asset.optString("browser_download_url")
                    if (name.endsWith(".apk", true) && url.startsWith("https://github.com/") && asset.optLong("size") > 100000L) {
                        return ApkRelease(
                            version = release.optString("tag_name", release.optString("name")),
                            url = url,
                            name = release.stringOrEmpty("name"),
                            body = release.stringOrEmpty("body"),
                            publishedAt = release.stringOrEmpty("published_at"),
                            htmlUrl = release.stringOrEmpty("html_url"),
                            size = asset.optLong("size")
                        )
                    }
                }
            }
            error("Tidak ditemukan aset .apk valid untuk kanal ${normalizedChannel.uppercase()}.")
        } finally { conn.disconnect() }
    }
    private fun nums(v: String): List<Int> = Regex("\\d+").findAll(v).mapNotNull { it.value.toIntOrNull() }.toList()

    private fun newer(latest: String, current: String): Boolean {
        val a = nums(latest); val b = nums(current)
        if (a.isEmpty()) return latest.removePrefix("v") != current.removePrefix("v")
        for (i in 0 until maxOf(a.size, b.size)) {
            val x = a.getOrElse(i) { 0 }; val y = b.getOrElse(i) { 0 }
            if (x != y) return x > y
        }
        return false
    }

    private fun installedVersion(): String = packageManager.getPackageInfo(packageName, 0).versionName ?: "0"

    private fun openDownloadConnection(url: String, range: String?): HttpURLConnection {
        val conn = URL(url).openConnection() as HttpURLConnection
        conn.connectTimeout = 15000
        conn.readTimeout = 30000
        conn.instanceFollowRedirects = true
        conn.setRequestProperty("User-Agent", "IRA-ZTE-Live-Signal-Charts-Android")
        // Tanpa kompresi transparan agar Content-Length dan rentang byte (Range) akurat.
        conn.setRequestProperty("Accept-Encoding", "identity")
        if (range != null) conn.setRequestProperty("Range", range)
        return conn
    }

    // Unduh satu koneksi (cadangan bila server tidak mendukung Range atau unduhan paralel gagal).
    private fun downloadSingle(url: String, target: File, onProgress: (Long, Long) -> Unit) {
        val conn = openDownloadConnection(url, null)
        try {
            if (conn.responseCode !in 200..299) error("Unduhan gagal: HTTP ${conn.responseCode}")
            val total = (conn.getHeaderField("Content-Length")?.toLongOrNull() ?: -1L).coerceAtLeast(0L)
            var downloaded = 0L
            conn.inputStream.use { input ->
                target.outputStream().use { output ->
                    val buffer = ByteArray(256 * 1024)
                    while (true) {
                        val count = input.read(buffer)
                        if (count < 0) break
                        output.write(buffer, 0, count)
                        downloaded += count
                        onProgress(downloaded, total)
                    }
                }
            }
        } finally { conn.disconnect() }
    }

    // Mengunduh satu rentang byte dan menulisnya langsung ke posisi yang tepat di file tujuan.
    private fun fetchRange(url: String, start: Long, end: Long, channel: FileChannel, buffer: ByteArray, downloaded: AtomicLong) {
        val conn = openDownloadConnection(url, "bytes=$start-$end")
        var counted = 0L
        try {
            if (conn.responseCode != HttpURLConnection.HTTP_PARTIAL) error("Server tidak mendukung Range (HTTP ${conn.responseCode})")
            var position = start
            conn.inputStream.use { input ->
                while (true) {
                    val count = input.read(buffer)
                    if (count < 0) break
                    if (position + count > end + 1) error("Server mengirim data melebihi rentang yang diminta")
                    val chunk = ByteBuffer.wrap(buffer, 0, count)
                    var written = 0
                    while (chunk.hasRemaining()) {
                        written += channel.write(chunk, position + written)
                    }
                    position += count
                    counted += count
                    downloaded.addAndGet(count.toLong())
                }
            }
            if (position != end + 1) error("Rentang data tidak lengkap")
        } catch (e: Exception) {
            downloaded.addAndGet(-counted)
            throw e
        } finally { conn.disconnect() }
    }

    // CDN GitHub sering membatasi kecepatan per koneksi; beberapa koneksi paralel (HTTP Range) biasanya jauh lebih cepat.
    private fun downloadParallel(url: String, total: Long, target: File, onProgress: (Long, Long) -> Unit) {
        val blockSize = 4L * 1024 * 1024
        val blocks = ((total + blockSize - 1) / blockSize).toInt()
        val nextBlock = AtomicInteger(0)
        val downloaded = AtomicLong(0L)
        val failure = AtomicReference<Exception?>(null)

        RandomAccessFile(target, "rw").use { file ->
            file.setLength(total)
            val channel = file.channel
            val workers = (0 until minOf(4, blocks)).map {
                Thread {
                    val buffer = ByteArray(64 * 1024)
                    try {
                        while (failure.get() == null) {
                            val index = nextBlock.getAndIncrement()
                            if (index >= blocks) break
                            val start = index * blockSize
                            val end = minOf(start + blockSize, total) - 1
                            var attempt = 0
                            while (true) {
                                try {
                                    fetchRange(url, start, end, channel, buffer, downloaded)
                                    break
                                } catch (e: Exception) {
                                    attempt++
                                    if (attempt >= 3 || failure.get() != null) throw e
                                    Thread.sleep(500L * attempt)
                                }
                            }
                        }
                    } catch (e: Exception) {
                        failure.compareAndSet(null, e)
                    }
                }
            }
            workers.forEach { it.start() }
            while (workers.any { it.isAlive }) {
                onProgress(downloaded.get(), total)
                Thread.sleep(250)
            }
            workers.forEach { it.join() }
        }
        failure.get()?.let { throw it }
        if (downloaded.get() != total) error("Ukuran unduhan tidak sesuai")
        onProgress(total, total)
    }

    private fun downloadApk(url: String, target: File, onProgress: (Long, Long) -> Unit) {
        var total = -1L
        var finalUrl = url
        var ranged = false
        try {
            val probe = openDownloadConnection(url, "bytes=0-0")
            try {
                val code = probe.responseCode
                if (code == HttpURLConnection.HTTP_PARTIAL) {
                    total = probe.getHeaderField("Content-Range")?.substringAfterLast('/')?.toLongOrNull() ?: -1L
                    ranged = total > 0
                    finalUrl = probe.url.toString()
                }
            } finally { probe.disconnect() }
        } catch (e: Exception) {
            ranged = false
        }
        if (ranged && total >= 2L * 1024 * 1024) {
            try {
                downloadParallel(finalUrl, total, target, onProgress)
                return
            } catch (e: Exception) {
                target.delete()
            }
        }
        downloadSingle(url, target, onProgress)
    }

    private fun installApk(release: ApkRelease) {
        val apk = File(cacheDir, "ira-zte-update.apk")
        val startedAt = System.nanoTime()
        var lastUpdateAt = startedAt
        downloadApk(release.url, apk) { downloaded, total ->
            val now = System.nanoTime()
            if (now - lastUpdateAt >= 300_000_000L || (total > 0 && downloaded >= total)) {
                val elapsed = (now - startedAt) / 1_000_000_000.0
                val speed = if (elapsed > 0) downloaded / elapsed else 0.0
                val eta = if (total > 0 && speed > 0) ((total - downloaded) / speed).toLong() else -1L
                val percent = if (total > 0) (downloaded * 100.0 / total).coerceIn(0.0, 100.0) else -1.0
                progress(percent, downloaded, total, speed.toLong(), eta)
                lastUpdateAt = now
            }
        }
        progress(100.0, apk.length(), apk.length(), 0L, 0L)
        if (apk.length() < 100000L) { apk.delete(); error("File APK tidak valid atau tidak lengkap.") }
            runOnUiThread {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O && !packageManager.canRequestPackageInstalls()) {
                    startActivity(Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:$packageName")))
                    status("APK diunduh. Izinkan pemasangan dari sumber ini, lalu coba lagi.")
                    downloadDone(false, "APK sudah diunduh. Izinkan pemasangan dari sumber ini di layar yang terbuka, lalu kembali ke aplikasi dan tekan Coba lagi.")
                    return@runOnUiThread
                }
                val uri = FileProvider.getUriForFile(this, "$packageName.fileprovider", apk)
                try {
                    startActivity(Intent(Intent.ACTION_VIEW).apply {
                        setDataAndType(uri, "application/vnd.android.package-archive")
                        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK)
                    })
                    status("APK siap dipasang. Ikuti konfirmasi Android.")
                    downloadDone(true, "Unduhan selesai. Ikuti layar pemasangan Android untuk menyelesaikan pembaruan.")
                } catch (e: Exception) {
                    status("Gagal membuka pemasang: ${e.localizedMessage}")
                    downloadDone(false, "Gagal membuka pemasang: ${e.localizedMessage ?: e.javaClass.simpleName}")
                }
            }
    }

    inner class RouterBridge {
        @JavascriptInterface
        fun checkForApkUpdate(channel: String?) {
            val selectedChannel = if (channel.equals("beta", true)) "beta" else "stable"
            Thread {
                try {
                    val release = latestApk(selectedChannel)
                    val current = installedVersion()
                    val isNewer = newer(release.version, current)
                    val label = selectedChannel.uppercase()
                    status(
                        if (isNewer) "Update $label tersedia: ${release.version} (terpasang: $current)."
                        else "Aplikasi sudah terbaru untuk kanal $label ($current). Release: ${release.version}."
                    )
                    updateResultToJs(JSONObject().apply {
                        put("update_available", isNewer)
                        put("current_version", current)
                        put("tag_name", release.version)
                        put("name", release.name)
                        put("body", release.body)
                        put("published_at", release.publishedAt)
                        put("html_url", release.htmlUrl)
                        put("channel", selectedChannel)
                        put("asset_size", release.size)
                        put("message", if (isNewer) "Update tersedia." else "Aplikasi sudah menggunakan versi terbaru untuk kanal $label.")
                    })
                } catch (e: Exception) {
                    val message = "Gagal memeriksa update: ${e.localizedMessage ?: "kesalahan jaringan"}"
                    status(message)
                    updateResultToJs(JSONObject().apply {
                        put("update_available", false)
                        put("error", message)
                    })
                }
            }.start()
        }

        @JavascriptInterface
        fun downloadAndInstallApk(channel: String?) {
            val selectedChannel = if (channel.equals("beta", true)) "beta" else "stable"
            Thread {
                try {
                    val release = latestApk(selectedChannel)
                    if (!newer(release.version, installedVersion())) {
                        val message = "Tidak ada APK ${selectedChannel.uppercase()} yang lebih baru."
                        status(message)
                        downloadDone(false, message)
                        return@Thread
                    }
                    installApk(release)
                } catch (e: Exception) {
                    val message = "Gagal mengunduh APK: ${e.localizedMessage ?: "kesalahan jaringan"}"
                    status(message)
                    downloadDone(false, message)
                }
            }.start()
        }

        @JavascriptInterface
        fun exportDiagnosticLogs(json: String?) {
            Thread {
                try {
                    val report = json?.takeIf { it.isNotBlank() } ?: error("Log kosong.")
                    val stamp = SimpleDateFormat("yyyyMMdd-HHmmss", Locale.US).format(Date())
                    val fileName = "ira-zte-diagnostic-$stamp.json"
                    val file = File(cacheDir, fileName)
                    file.writeText(report, Charsets.UTF_8)
                    // Salinan permanen di Download/IRA ZTE (Android 10+).
                    val savedPath = saveToDownloads(fileName, report)
                    val uri = FileProvider.getUriForFile(this@MainActivity, "$packageName.fileprovider", file)
                    val share = Intent(Intent.ACTION_SEND).apply {
                        type = "application/json"
                        putExtra(Intent.EXTRA_STREAM, uri)
                        putExtra(Intent.EXTRA_SUBJECT, "IRA ZTE diagnostic log")
                        putExtra(Intent.EXTRA_TEXT, "Log diagnostik IRA ZTE. Periksa isi file sebelum membagikannya.")
                        clipData = ClipData.newUri(contentResolver, file.name, uri)
                        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
                    }
                    runOnUiThread {
                        val shared = try {
                            startActivity(Intent.createChooser(share, "Simpan atau bagikan log debug"))
                            true
                        } catch (e: Exception) {
                            false
                        }
                        when {
                            savedPath != null -> exportResult(true, "Log disimpan di $savedPath" + if (shared) ". Pilih aplikasi untuk membagikannya." else ".")
                            shared -> exportResult(true, "Pilih tujuan penyimpanan atau aplikasi untuk membagikan log.")
                            else -> exportResult(false, "Tidak bisa menyimpan atau membagikan log di perangkat ini.")
                        }
                    }
                } catch (e: Exception) {
                    exportResult(false, "Gagal ekspor log: ${e.localizedMessage ?: e.javaClass.simpleName}")
                }
            }.start()
        }

        // Membuka tautan GitHub di peramban sistem (bukan di dalam WebView aplikasi).
        @JavascriptInterface
        fun openUrl(url: String?) {
            val target = url?.trim().orEmpty()
            if (!target.startsWith("https://github.com/")) return
            runOnUiThread {
                try {
                    startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(target)))
                } catch (e: Exception) {
                    // Tidak ada peramban: abaikan.
                }
            }
        }

        @JavascriptInterface
        fun getAppVersion(): String = installedVersion()

        @JavascriptInterface
        fun pingHost(host: String?): Int {
            val target = host?.trim().orEmpty()
            if (target.isEmpty() || target.length > 253 || target.startsWith("-") ||
                !target.matches(Regex("[A-Za-z0-9.-]+"))) return -1
            return try {
                val process = ProcessBuilder("ping", "-c", "1", "-W", "2", target)
                    .redirectErrorStream(true).start()
                val output = process.inputStream.bufferedReader().use { it.readText() }
                val exitCode = process.waitFor()
                if (exitCode != 0) -1
                else Regex("time[=<]([0-9.]+)").find(output)?.groupValues?.get(1)?.toDoubleOrNull()?.toInt() ?: 0
            } catch (_: Exception) { -1 }
        }

        @JavascriptInterface
        fun getRouterData(): String {
            val data = JSONObject()
            try {
                val url = URL("http://192.168.0.1/ubus/?t=${System.currentTimeMillis()}")
                val connection = (url.openConnection() as HttpURLConnection).apply {
                    requestMethod = "POST"; connectTimeout = 3000; readTimeout = 3000; doOutput = true
                    setRequestProperty("Content-Type", "application/json")
                    setRequestProperty("Referer", "http://192.168.0.1/index.html")
                    setRequestProperty("Origin", "http://192.168.0.1")
                    setRequestProperty("User-Agent", "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/130.0 Mobile Safari/537.36")
                    setRequestProperty("z-mode", "0"); setRequestProperty("z-tag", "nwinfo_get_netinfo")
                    setRequestProperty("X-Requested-With", "XMLHttpRequest")
                }
                val payload = """[{"jsonrpc":"2.0","method":"call","params":["00000000000000000000000000000000","zte_nwinfo_api","nwinfo_get_netinfo",{}],"id":1}]"""
                connection.outputStream.use { it.write(payload.toByteArray(Charsets.UTF_8)) }
                val array = JSONArray(connection.inputStream.bufferedReader().use { it.readText() })
                val telemetry = array.optJSONObject(0)?.optJSONArray("result")?.optJSONObject(1)
                if (telemetry != null) {
                    val keys = telemetry.keys()
                    while (keys.hasNext()) { val key = keys.next(); data.put(key, telemetry.opt(key)) }
                }
                connection.disconnect()
            } catch (_: Exception) { }
            data.put("internet_ok", checkInternet())
            return data.toString()
        }

        private fun checkInternet(): Boolean = try {
            val connection = URL("http://1.1.1.1").openConnection() as HttpURLConnection
            connection.connectTimeout = 1500; connection.readTimeout = 1500
            connection.connect(); connection.disconnect(); true
        } catch (_: Exception) { false }
    }
}
