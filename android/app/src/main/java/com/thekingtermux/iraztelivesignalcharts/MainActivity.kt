package com.thekingtermux.iraztelivesignalcharts

import android.annotation.SuppressLint
import android.app.Activity
import android.os.Bundle
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import org.json.JSONArray
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL

class MainActivity : Activity() {
    private lateinit var webView: WebView

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        webView = WebView(this)
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.webChromeClient = WebChromeClient()
        webView.webViewClient = WebViewClient()
        webView.addJavascriptInterface(RouterBridge(), "AndroidBridge")
        setContentView(webView)
        webView.loadUrl("file:///android_asset/index.html")
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) webView.goBack() else super.onBackPressed()
    }

    inner class RouterBridge {
        @JavascriptInterface
        fun getRouterData(): String {
            val data = JSONObject()
            try {
                val url = URL("http://192.168.0.1/ubus/?t=${System.currentTimeMillis()}")
                val connection = (url.openConnection() as HttpURLConnection).apply {
                    requestMethod = "POST"
                    connectTimeout = 3000
                    readTimeout = 3000
                    doOutput = true
                    setRequestProperty("Content-Type", "application/json")
                    setRequestProperty("Referer", "http://192.168.0.1/index.html")
                    setRequestProperty("Origin", "http://192.168.0.1")
                    setRequestProperty("User-Agent", "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/130.0 Mobile Safari/537.36")
                    setRequestProperty("z-mode", "0")
                    setRequestProperty("z-tag", "nwinfo_get_netinfo")
                    setRequestProperty("X-Requested-With", "XMLHttpRequest")
                }
                val payload = """[{"jsonrpc":"2.0","method":"call","params":["00000000000000000000000000000000","zte_nwinfo_api","nwinfo_get_netinfo",{}],"id":1}]"""
                connection.outputStream.use { it.write(payload.toByteArray(Charsets.UTF_8)) }
                val response = connection.inputStream.bufferedReader().use { it.readText() }
                val array = JSONArray(response)
                val result = array.optJSONObject(0)?.optJSONArray("result")
                val telemetry = result?.optJSONObject(1)
                if (telemetry != null) {
                    val keys = telemetry.keys()
                    while (keys.hasNext()) {
                        val key = keys.next()
                        data.put(key, telemetry.opt(key))
                    }
                }
                connection.disconnect()
            } catch (_: Exception) {
                // Return the connectivity flag even if router telemetry is unavailable.
            }
            data.put("internet_ok", checkInternet())
            return data.toString()
        }

        private fun checkInternet(): Boolean {
            return try {
                val connection = URL("http://1.1.1.1").openConnection() as HttpURLConnection
                connection.connectTimeout = 1500
                connection.readTimeout = 1500
                connection.connect()
                connection.disconnect()
                true
            } catch (_: Exception) {
                false
            }
        }
    }
}
