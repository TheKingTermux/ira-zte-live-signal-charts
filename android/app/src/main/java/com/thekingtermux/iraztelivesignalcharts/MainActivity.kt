package com.thekingtermux.iraztelivesignalcharts

import android.annotation.SuppressLint
import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.core.content.FileProvider
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.net.HttpURLConnection
import java.net.URL

class MainActivity : Activity() {
    private lateinit var webView: WebView
    private val repository = "TheKingTermux/ira-zte-live-signal-charts"

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        webView = WebView(this)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.webChromeClient = WebChromeClient()
        webView.webViewClient = object : WebViewClient() {
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                webView.evaluateJavascript("""
                    (function() {
                      if (document.getElementById('android-apk-updater')) return;
                      const box = document.getElementById('settingsBox');
                      if (!box) return;
                      const section = document.createElement('div');
                      section.id = 'android-apk-updater';
                      section.className = 'pt-3 border-t border-slate-800 space-y-2';
                      section.innerHTML = '<div class="text-xs font-bold text-cyan-400">Pembaruan APK Android</div>' +
                        '<button id="apk-check-btn" class="w-full bg-slate-800 text-white text-xs px-3 py-2 rounded-xl">Periksa Pembaruan APK</button>' +
                        '<div id="apk-update-status" class="text-[10px] text-slate-400"></div>' +
                        '<div id="apk-progress-panel" class="hidden space-y-1.5 rounded-lg border border-slate-800 bg-slate-950/70 p-2">' +
                          '<div class="flex justify-between gap-2 text-[10px]"><span id="apk-progress-label">Menyiapkan unduhan…</span><span id="apk-progress-percent">0%</span></div>' +
                          '<div class="h-2 overflow-hidden rounded-full bg-slate-800"><div id="apk-progress-bar" class="h-full w-0 rounded-full bg-cyan-500"></div></div>' +
                          '<div id="apk-progress-details" class="text-[10px] text-slate-400">Menghitung kecepatan dan sisa waktu…</div></div>';
                      const closeRow = box.querySelector('.pt-2.flex.justify-end');
                      if (closeRow) box.insertBefore(section, closeRow); else box.appendChild(section);
                      document.getElementById('apk-check-btn').onclick = function() {
                        document.getElementById('apk-update-status').textContent = 'Memeriksa GitHub Releases...';
                        AndroidBridge.checkForApkUpdate();
                      };
                    })();
                """.trimIndent(), null)
            }
        }
        webView.addJavascriptInterface(RouterBridge(), "AndroidBridge")
        setContentView(webView)
        webView.loadUrl("file:///android_asset/index.html")
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

    private fun progress(percent: Double, downloaded: Long, total: Long, speed: Long, eta: Long) {
        val percentJs = if (percent < 0) "null" else percent.toString()
        val script = """
            (function() {
              const panel = document.getElementById('apk-progress-panel');
              if (!panel) return;
              panel.classList.remove('hidden');
              const p = $percentJs;
              document.getElementById('apk-progress-label').textContent = 'Mengunduh APK…';
              document.getElementById('apk-progress-percent').textContent = p === null ? '—' : Math.floor(p) + '%';
              document.getElementById('apk-progress-bar').style.width = (p === null ? 0 : p) + '%';
              const fmt = n => { if (!n) return '0 B'; const u = ['B','KB','MB','GB']; let i=0,v=n; while(v>=1024&&i<u.length-1){v/=1024;i++;} return (i===0?Math.round(v):v.toFixed(1))+' '+u[i]; };
              const eta = $eta;
              const etaText = eta < 0 ? 'menghitung…' : eta < 60 ? eta + ' dtk' : Math.floor(eta/60)+' m '+(eta%60)+' dtk';
              document.getElementById('apk-progress-details').textContent = fmt($downloaded) + ' / ' + ($total > 0 ? fmt($total) : 'ukuran tidak diketahui') + ' · ' + fmt($speed) + '/dtk · Sisa ' + etaText;
            })();
        """.trimIndent()
        runOnUiThread { webView.evaluateJavascript(script, null) }
    }

    private data class ApkRelease(val version: String, val url: String)

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
                        return ApkRelease(release.optString("tag_name", release.optString("name")), url)
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

    private fun installApk(release: ApkRelease) {
        val conn = (URL(release.url).openConnection() as HttpURLConnection).apply {
            connectTimeout = 15000; readTimeout = 30000; instanceFollowRedirects = true
            setRequestProperty("User-Agent", "IRA-ZTE-Live-Signal-Charts-Android")
        }
        try {
            if (conn.responseCode !in 200..299) error("Unduhan gagal: HTTP ${conn.responseCode}")
            val apk = File(cacheDir, "ira-zte-update.apk")
            val total = (conn.getHeaderField("Content-Length")?.toLongOrNull() ?: -1L).coerceAtLeast(0L)
            val startedAt = System.nanoTime()
            var downloaded = 0L
            var lastUpdateAt = startedAt
            conn.inputStream.use { input ->
                apk.outputStream().use { output ->
                    val buffer = ByteArray(64 * 1024)
                    while (true) {
                        val count = input.read(buffer)
                        if (count < 0) break
                        output.write(buffer, 0, count)
                        downloaded += count
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
                }
            }
            progress(100.0, downloaded, total, 0L, 0L)
            if (apk.length() < 100000L) { apk.delete(); error("File APK tidak valid atau tidak lengkap.") }
            runOnUiThread {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O && !packageManager.canRequestPackageInstalls()) {
                    startActivity(Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:$packageName")))
                    status("APK diunduh. Izinkan pemasangan dari sumber ini, lalu coba lagi.")
                    return@runOnUiThread
                }
                val uri = FileProvider.getUriForFile(this, "$packageName.fileprovider", apk)
                try {
                    startActivity(Intent(Intent.ACTION_VIEW).apply {
                        setDataAndType(uri, "application/vnd.android.package-archive")
                        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK)
                    })
                    status("APK siap dipasang. Ikuti konfirmasi Android.")
                } catch (e: Exception) { status("Gagal membuka pemasang: ${e.localizedMessage}") }
            }
        } finally { conn.disconnect() }
    }

    inner class RouterBridge {
        @JavascriptInterface
        fun checkForApkUpdate(channel: String?) {
            val selectedChannel = if (channel.equals("beta", true)) "beta" else "stable"
            Thread {
                try {
                    val release = latestApk(selectedChannel)
                    val current = installedVersion()
                    if (newer(release.version, current)) status("Update ${selectedChannel.uppercase()} tersedia: ${release.version} (terpasang: $current).", true)
                    else status("Aplikasi sudah terbaru untuk kanal ${selectedChannel.uppercase()} ($current). Release: ${release.version}.")
                } catch (e: Exception) { status("Gagal memeriksa update: ${e.localizedMessage ?: "kesalahan jaringan"}") }
            }.start()
        }

        @JavascriptInterface
        fun downloadAndInstallApk(channel: String?) {
            val selectedChannel = if (channel.equals("beta", true)) "beta" else "stable"
            Thread {
                try {
                    val release = latestApk(selectedChannel)
                    if (!newer(release.version, installedVersion())) { status("Tidak ada APK ${selectedChannel.uppercase()} yang lebih baru."); return@Thread }
                    installApk(release)
                } catch (e: Exception) { status("Gagal mengunduh APK: ${e.localizedMessage ?: "kesalahan jaringan"}") }
            }.start()
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
