import time
import threading
import subprocess
import platform
import requests
import webview
import urllib3
import os
import sys
import tempfile
from pathlib import Path

APP_VERSION = "1.1-dev.3"
GITHUB_REPOSITORY = "TheKingTermux/ira-zte-live-signal-charts"
GITHUB_RELEASES_API = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/releases?per_page=30"

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>IRA ZTE MC8501 5G LIVE SIGNAL CHARTS</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .modal-transition {
            transition: opacity 0.25s ease-in-out, transform 0.25s ease-in-out;
        }
        .accordion-content {
            transition: max-height 0.3s ease-in-out, opacity 0.3s ease-in-out;
            max-height: 0;
            opacity: 0;
            overflow: hidden;
        }
        .accordion-content.open {
            max-height: 300px;
            opacity: 1;
        }
        #settingsBox {
            height: auto;
            max-height: 92vh;
            transition: height 0.32s cubic-bezier(0.22, 1, 0.36, 1), transform 0.25s ease-in-out;
        }
        #settingsContent {
            flex: 0 0 auto;
            height: 0;
            max-height: calc(92vh - 190px);
            transition: height 0.32s cubic-bezier(0.22, 1, 0.36, 1);
            will-change: height;
        }
        .tab-pane {
            transition: opacity 0.24s cubic-bezier(0.22, 1, 0.36, 1), transform 0.24s cubic-bezier(0.22, 1, 0.36, 1);
            will-change: opacity, transform;
            scrollbar-gutter: stable;
        }
        @media (max-height: 600px) {
            #settingsContent { max-height: calc(92vh - 165px); }
        }
        @media (prefers-reduced-motion: reduce) {
            #settingsBox, #settingsContent, .tab-pane { transition-duration: 0.01ms; }
        }
    </style>
</head>
<body id="app-body" class="bg-slate-950 text-slate-100 h-screen overflow-hidden p-4 flex flex-col justify-between select-none relative">
    
    <!-- Header -->
    <header class="flex justify-between items-center pb-2 border-b border-slate-800 gap-2 shrink-0 relative">
        <div>
            <h1 class="text-lg font-black tracking-wider text-cyan-400 flex items-center gap-2">
                <span class="relative flex h-2.5 w-2.5">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
                </span>
                IRA ZTE MC8501 5G LIVE SIGNAL CHARTS
            </h1>
            <p class="text-[10px] text-slate-400">Real-time Telemetry & Smart Network Diagnostic Dashboard</p>
        </div>
        <div class="flex items-center gap-2">
            <!-- Settings Button -->
            <button onclick="animateButton(this); toggleSettingsModal()" class="bg-slate-900 border border-slate-800 hover:border-cyan-500 p-2 rounded-xl text-cyan-400 flex items-center justify-center shadow-inner active:scale-95 transition-transform" title="Pengaturan & Ping Tool">
                ⚙️
            </button>
            <!-- Bell History Button -->
            <button onclick="animateButton(this); toggleHistoryModal()" class="relative bg-slate-900 border border-slate-800 hover:border-cyan-500 p-2 rounded-xl text-cyan-400 flex items-center justify-center shadow-inner active:scale-95 transition-transform" title="Riwayat Koneksi Jaringan">
                🔔
                <span id="bell-badge" class="absolute -top-1 -right-1 bg-red-500 text-white text-[9px] font-bold px-1.5 py-0.2 rounded-full hidden animate-pulse">0</span>
            </button>
            <div id="status-conn" class="text-[11px] font-medium bg-slate-900 border border-slate-800 px-3 py-1 rounded-xl text-slate-400 shadow-inner">
                Menghubungkan...
            </div>
        </div>
    </header>

    <!-- Floating Animated Notification Banner -->
    <div class="w-full flex justify-center shrink-0 my-1">
        <div id="floating-alert" class="hidden bg-orange-600/90 border border-orange-400 text-white px-4 py-1 rounded-xl shadow-2xl animate-bounce flex items-center gap-2 text-xs font-bold backdrop-blur-md z-40">
            <span id="floating-alert-text">⚠️ KONEKSI TOWER TERPUTUS!</span>
        </div>
    </div>

    <!-- Main Dashboard Grid -->
    <main class="space-y-2 flex-grow flex flex-col justify-center my-auto">
        
        <!-- 4 Compact Horizontal Cards -->
        <div class="grid grid-cols-1 gap-2">
            
            <!-- RSRP Row Card -->
            <div class="card-bg bg-slate-900/80 border border-slate-800/80 px-3.5 py-1.5 rounded-xl shadow-md flex items-center justify-between gap-4">
                <div class="w-48 shrink-0 flex flex-col justify-center">
                    <div class="flex items-center justify-between">
                        <span class="text-[11px] font-semibold text-cyan-400 uppercase tracking-wider">5G RSRP</span>
                        <div id="status-rsrp" class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[10px] font-semibold">
                            <span class="h-1.5 w-1.5 rounded-full bg-slate-500" id="dot-rsrp"></span>
                            <span id="text-rsrp">Memuat</span>
                        </div>
                    </div>
                    <span class="text-[9px] text-slate-400 -mt-0.5">Daya Terima Sinyal</span>
                    <div id="val-rsrp" class="text-base font-bold text-slate-100 leading-tight">- dBm</div>
                </div>
                <div class="h-12 w-full relative flex-grow">
                    <canvas id="chartRsrp"></canvas>
                </div>
            </div>

            <!-- RSSI Row Card -->
            <div class="card-bg bg-slate-900/80 border border-slate-800/80 px-3.5 py-1.5 rounded-xl shadow-md flex items-center justify-between gap-4">
                <div class="w-48 shrink-0 flex flex-col justify-center">
                    <div class="flex items-center justify-between">
                        <span class="text-[11px] font-semibold text-cyan-400 uppercase tracking-wider">5G RSSI</span>
                        <div id="status-rssi" class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[10px] font-semibold">
                            <span class="h-1.5 w-1.5 rounded-full bg-slate-500" id="dot-rssi"></span>
                            <span id="text-rssi">Memuat</span>
                        </div>
                    </div>
                    <span class="text-[9px] text-slate-400 -mt-0.5">Kekuatan Total & Derau</span>
                    <div id="val-rssi" class="text-base font-bold text-slate-100 leading-tight">- dBm</div>
                </div>
                <div class="h-12 w-full relative flex-grow">
                    <canvas id="chartRssi"></canvas>
                </div>
            </div>

            <!-- RSRQ Row Card -->
            <div class="card-bg bg-slate-900/80 border border-slate-800/80 px-3.5 py-1.5 rounded-xl shadow-md flex items-center justify-between gap-4">
                <div class="w-48 shrink-0 flex flex-col justify-center">
                    <div class="flex items-center justify-between">
                        <span class="text-[11px] font-semibold text-cyan-400 uppercase tracking-wider">5G RSRQ</span>
                        <div id="status-rsrq" class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[10px] font-semibold">
                            <span class="h-1.5 w-1.5 rounded-full bg-slate-500" id="dot-rsrq"></span>
                            <span id="text-rsrq">Memuat</span>
                        </div>
                    </div>
                    <span class="text-[9px] text-slate-400 -mt-0.5">Kualitas Sinyal</span>
                    <div id="val-rsrq" class="text-base font-bold text-slate-100 leading-tight">- dB</div>
                </div>
                <div class="h-12 w-full relative flex-grow">
                    <canvas id="chartRsrq"></canvas>
                </div>
            </div>

            <!-- SINR / SNR Row Card -->
            <div class="card-bg bg-slate-900/80 border border-slate-800/80 px-3.5 py-1.5 rounded-xl shadow-md flex items-center justify-between gap-4">
                <div class="w-48 shrink-0 flex flex-col justify-center">
                    <div class="flex items-center justify-between">
                        <span class="text-[11px] font-semibold text-cyan-400 uppercase tracking-wider">5G SINR / SNR</span>
                        <div id="status-sinr" class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[10px] font-semibold">
                            <span class="h-1.5 w-1.5 rounded-full bg-slate-500" id="dot-sinr"></span>
                            <span id="text-sinr">Memuat</span>
                        </div>
                    </div>
                    <span class="text-[9px] text-slate-400 -mt-0.5">Kebersihan Sinyal</span>
                    <div id="val-sinr" class="text-base font-bold text-slate-100 leading-tight">- dB</div>
                </div>
                <div class="h-12 w-full relative flex-grow">
                    <canvas id="chartSinr"></canvas>
                </div>
            </div>

        </div>

            <!-- Internet Ping Card -->
            <div class="card-bg bg-slate-900/80 border border-slate-800/80 px-3.5 py-1.5 rounded-xl shadow-md flex items-center justify-between gap-4">
                <div class="w-48 shrink-0 flex flex-col justify-center">
                    <div class="flex items-center justify-between">
                        <span class="text-[11px] font-semibold text-cyan-400 uppercase tracking-wider">INTERNET PING</span>
                        <div id="status-ping" class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[10px] font-semibold">
                            <span class="h-1.5 w-1.5 rounded-full bg-slate-500" id="dot-ping"></span>
                            <span id="text-ping">Menunggu</span>
                        </div>
                    </div>
                    <span id="ping-chart-title" class="text-[9px] text-slate-400 -mt-0.5">📈 Ping Latency</span>
                    <div id="val-ping" class="text-base font-bold text-slate-100 leading-tight">— ms</div>
                </div>
                <div class="h-12 w-full relative flex-grow">
                    <canvas id="chartPing"></canvas>
                </div>
            </div>

        <!-- Tower Information Panel (Tanpa Animasi) -->
        <div class="card-bg bg-slate-900/90 border border-slate-800/80 p-2.5 rounded-xl shadow-md">
            <h2 class="text-xs font-bold text-cyan-400 mb-1.5 flex items-center gap-1.5">
                🗼 TOWER & NETWORK INFORMATION
            </h2>
            <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2">
                
                <div class="sub-card bg-slate-950/60 p-2 rounded-lg border border-slate-800/60">
                    <div class="text-[9px] uppercase font-semibold text-slate-400">Tower Status</div>
                    <div id="tower-status-val" class="text-[11px] font-bold text-emerald-400 mt-0.5 truncate">Tersambung</div>
                </div>

                <div class="sub-card bg-slate-950/60 p-2 rounded-lg border border-slate-800/60">
                    <div class="text-[9px] uppercase font-semibold text-slate-400">Internet Status</div>
                    <div id="internet-status-val" class="text-[11px] font-bold text-emerald-400 mt-0.5 truncate">Normal</div>
                </div>

                <div class="sub-card bg-slate-950/60 p-2 rounded-lg border border-slate-800/60">
                    <div class="text-[9px] uppercase font-semibold text-slate-400">Cell PCI 5G</div>
                    <div id="info-pci" class="text-[11px] font-bold text-slate-100 mt-0.5">-</div>
                </div>

                <div class="sub-card bg-slate-950/60 p-2 rounded-lg border border-slate-800/60">
                    <div class="text-[9px] uppercase font-semibold text-slate-400">Cell ID 5G</div>
                    <div id="info-cellid" class="text-[11px] font-bold text-cyan-300 mt-0.5 truncate">-</div>
                </div>

                <div class="sub-card bg-slate-950/60 p-2 rounded-lg border border-slate-800/60">
                    <div class="text-[9px] uppercase font-semibold text-slate-400">Network Type</div>
                    <div id="info-nettype" class="text-[11px] font-bold text-emerald-400 mt-0.5">-</div>
                </div>

                <div class="sub-card bg-slate-950/60 p-2 rounded-lg border border-slate-800/60">
                    <div class="text-[9px] uppercase font-semibold text-slate-400">Signal Bar</div>
                    <div id="info-signalbar" class="text-[11px] font-bold text-slate-100 mt-0.5">- / 3</div>
                </div>

                <div class="sub-card bg-slate-950/60 p-2 rounded-lg border border-slate-800/60">
                    <div class="text-[9px] uppercase font-semibold text-slate-400">Active Band</div>
                    <div id="info-band" class="text-[11px] font-bold text-cyan-400 mt-0.5">-</div>
                </div>

            </div>
        </div>

        <!-- Signal Rating Criteria Accordion (Dropdown Initially Hidden) -->
        <div class="card-bg bg-slate-900/90 border border-slate-800/80 rounded-xl shadow-md overflow-hidden">
            <button onclick="toggleAccordion()" class="w-full p-2.5 flex justify-between items-center text-xs font-bold text-cyan-400 bg-slate-900/50 hover:bg-slate-800/50 transition-colors">
                <span class="flex items-center gap-1.5">📊 Kriteria Penilaian Kualitas Sinyal 5G</span>
                <span id="accordion-arrow" class="text-slate-400 transition-transform duration-300">▼</span>
            </button>
            <div id="accordion-content" class="accordion-content px-3 pb-2">
                <div class="overflow-x-auto border-t border-slate-800/60 pt-2">
                    <table class="w-full text-left text-[10px] text-slate-300 border-collapse">
                        <thead>
                            <tr class="border-b border-slate-800 text-slate-400 uppercase">
                                <th class="py-1 px-2">Parameter</th>
                                <th class="py-1 px-2 text-purple-400">🟣 Mantap</th>
                                <th class="py-1 px-2 text-emerald-500">🟢 Bagus</th>
                                <th class="py-1 px-2 text-amber-400">🟡 Cukup</th>
                                <th class="py-1 px-2 text-red-400">🔴 Buruk</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-800/50">
                            <tr>
                                <td class="py-1 px-2 font-semibold text-cyan-300">RSRP (Daya Sinyal)</td>
                                <td class="py-1 px-2">&ge; -80 dBm</td>
                                <td class="py-1 px-2">-81 s/d -95 dBm</td>
                                <td class="py-1 px-2">-96 s/d -110 dBm</td>
                                <td class="py-1 px-2">&lt; -110 dBm</td>
                            </tr>
                            <tr>
                                <td class="py-1 px-2 font-semibold text-cyan-300">RSSI (Kekuatan Total)</td>
                                <td class="py-1 px-2">&ge; -70 dBm</td>
                                <td class="py-1 px-2">-71 s/d -85 dBm</td>
                                <td class="py-1 px-2">-86 s/d -100 dBm</td>
                                <td class="py-1 px-2">&lt; -100 dBm</td>
                            </tr>
                            <tr>
                                <td class="py-1 px-2 font-semibold text-cyan-300">RSRQ (Kualitas Sinyal)</td>
                                <td class="py-1 px-2">&ge; -10 dB</td>
                                <td class="py-1 px-2">-11 s/d -15 dB</td>
                                <td class="py-1 px-2">-16 s/d -20 dB</td>
                                <td class="py-1 px-2">&lt; -20 dB</td>
                            </tr>
                            <tr>
                                <td class="py-1 px-2 font-semibold text-cyan-300">SINR / SNR (Kebersihan Sinyal)</td>
                                <td class="py-1 px-2">&ge; 20 dB</td>
                                <td class="py-1 px-2">10 s/d 19 dB</td>
                                <td class="py-1 px-2">0 s/d 9 dB</td>
                                <td class="py-1 px-2">&lt; 0 dB</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

    </main>

    <!-- Settings & Ping Tool Modal (Animated Open/Close + Clean Tab Transitions) -->
    <div id="settingsModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm opacity-0 pointer-events-none modal-transition">
        <div id="settingsBox" class="bg-slate-900 border border-slate-800 p-5 rounded-2xl max-w-2xl w-full mx-4 max-h-[92vh] overflow-hidden flex flex-col shadow-2xl text-slate-100 transform scale-95">
            <div class="flex justify-between items-center pb-2 border-b border-slate-800">
                <h3 class="text-sm font-bold text-cyan-400 flex items-center gap-2">⚙️ Pengaturan & Network Tools</h3>
                <button onclick="animateButton(this); toggleSettingsModal()" class="text-slate-400 hover:text-white text-xs font-bold px-2 py-1 rounded-lg bg-slate-800">✕</button>
            </div>
            
            <!-- Modal Tabs Header -->
            <div class="flex border-b border-slate-800 text-xs shrink-0">
                <button onclick="switchTab('tab-general')" id="btn-tab-general" class="flex-1 py-2 font-semibold text-cyan-400 border-b-2 border-cyan-400 bg-cyan-500/10 transition-all duration-300">Pengaturan Umum</button>
                <button onclick="switchTab('tab-ping')" id="btn-tab-ping" class="flex-1 py-2 font-semibold text-slate-400 border-b-2 border-transparent hover:text-slate-200 transition-all duration-300">Ping Tool</button>
                <button onclick="switchTab('tab-speed')" id="btn-tab-speed" class="flex-1 py-2 font-semibold text-slate-400 border-b-2 border-transparent hover:text-slate-200 transition-all duration-300">Speed Test</button>
                <button onclick="switchTab('tab-about')" id="btn-tab-about" class="flex-1 py-2 font-semibold text-slate-400 border-b-2 border-transparent hover:text-slate-200 transition-all duration-300">About</button>
            </div>

            <!-- Tab Contents Container -->
            <div id="settingsContent" class="relative min-h-0 overflow-hidden pr-1">
                <!-- Tab 1: General Settings -->
                <div id="tab-general" class="tab-pane absolute inset-0 w-full overflow-y-auto overscroll-contain space-y-3 pt-1 pr-1 opacity-100 scale-100 translate-y-0 pointer-events-auto">
                    <div>
                        <label class="text-[11px] font-semibold text-slate-300 block mb-1">Tema Tampilan</label>
                        <select id="setting-theme" onchange="changeTheme(this.value)" class="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 p-2 rounded-xl focus:outline-none focus:border-cyan-500 transition-all">
                            <option value="dark" selected>Gelap (Default)</option>
                            <option value="light">Terang</option>
                        </select>
                    </div>
                    <div class="rounded-xl border border-slate-800 bg-slate-950/50 p-3 space-y-2">
                        <div class="text-[11px] font-semibold text-slate-300">Notifikasi Gangguan Jaringan</div>
                        <label class="flex items-center gap-2 text-[11px] text-slate-300">
                            <input id="suppress-tower-popup" type="checkbox" onchange="savePopupPreferences()" class="accent-cyan-500">
                            Sembunyikan notifikasi saat tower bermasalah
                        </label>
                        <label class="flex items-center gap-2 text-[11px] text-slate-300">
                            <input id="suppress-internet-popup" type="checkbox" onchange="savePopupPreferences()" class="accent-cyan-500">
                            Sembunyikan notifikasi saat internet bermasalah
                        </label>
                        <button onclick="animateButton(this); resetPopupPreferences()" class="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-semibold px-3 py-2 rounded-lg transition-all">Reset Notifikasi Gangguan</button>
                        <p class="text-[10px] text-slate-500">Reset mengaktifkan kembali notifikasi gangguan tower dan internet. Notifikasi koneksi pulih tetap aktif.</p>
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-300 block mb-1">Frekuensi Update Data (Refresh Rate)</label>
                        <select id="setting-freq" onchange="changeFrequency(this.value)" class="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 p-2 rounded-xl focus:outline-none focus:border-cyan-500 transition-all">
                            <option value="1000" selected>Cepat / Default (1 Detik)</option>
                            <option value="2000">Normal (2 Detik)</option>
                            <option value="4000">Lambat (4 Detik)</option>
                        </select>
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-300 block mb-1">Frekuensi Grafik Ping Dashboard</label>
                        <select id="setting-ping-freq" onchange="changePingFrequency(this.value)" class="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 p-2 rounded-xl focus:outline-none focus:border-cyan-500 transition-all">
                            <option value="auto">Mengikuti update interval (×2)</option>
                            <option value="custom">Custom</option>
                        </select>
                        <input id="setting-ping-freq-custom" type="number" min="1" max="3600" step="1" placeholder="Interval custom (detik)" oninput="changePingFrequency('custom')" class="hidden mt-2 w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 p-2 rounded-xl focus:outline-none focus:border-cyan-500 transition-all">
                        <p class="text-[10px] text-slate-500 mt-1">Default mengikuti 2× interval refresh data. Custom: 1–3600 detik.</p>
                    </div>
                </div>

                <!-- Tab 2: Ping Tool -->
                <div id="tab-ping" class="tab-pane absolute inset-0 w-full overflow-y-auto overscroll-contain space-y-3 pt-1 pr-1 opacity-0 scale-[0.985] translate-y-1 pointer-events-none hidden">
                    <div>
                        <label class="text-[11px] font-semibold text-slate-300 block mb-1">Target Host / IP</label>
                        <div class="flex gap-2">
                            <input type="text" id="ping-host" value="1.1.1.1" class="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 p-2 rounded-xl focus:outline-none focus:border-cyan-500 transition-all">
                            <button onclick="animateButton(this); runPing(this)" id="btn-ping" class="bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded-xl text-xs font-semibold shrink-0 transition-all active:scale-95">Ping</button>
                        </div>
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-300 block mb-1">Hasil Ping</label>
                        <pre id="ping-output" class="w-full bg-slate-950 border border-slate-800 text-[10px] text-emerald-400 p-2.5 rounded-xl h-64 min-h-64 max-h-[48vh] overflow-y-auto font-mono whitespace-pre-wrap break-words">Menunggu perintah...</pre>
                    </div>
                </div>

                <!-- Tab 3: Animated Speed Test -->
                <div id="tab-speed" class="tab-pane absolute inset-0 w-full overflow-y-auto overscroll-contain space-y-3 pt-1 pr-1 opacity-0 scale-[0.985] translate-y-1 pointer-events-none hidden">
                    <div class="flex flex-wrap items-center justify-between gap-2">
                        <div>
                            <div class="text-sm font-bold text-cyan-300">⚡ Internet Speed Test</div>
                            <p class="text-[10px] text-slate-400">Tes berurutan: download 30 dtk → upload 30 dtk → latensi 30 dtk, dengan statistik min / rata-rata / maks.</p>
                        </div>
                        <button onclick="animateButton(this); runSpeedTest()" id="btn-speed-test" class="bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-2 rounded-xl text-xs font-semibold transition-all active:scale-95">▶ Mulai Speed Test</button>
                    </div>

                    <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
                        <div class="bg-slate-950 border border-slate-800 rounded-xl p-3">
                            <div class="text-[10px] text-slate-400">DOWNLOAD</div>
                            <div class="text-xl font-black text-cyan-300"><span id="speed-download">—</span><span class="text-xs font-semibold ml-1">Mbps</span></div>
                            <div id="speed-download-status" class="text-[9px] text-slate-500">Menunggu tes</div>
                        </div>
                        <div class="bg-slate-950 border border-slate-800 rounded-xl p-3">
                            <div class="text-[10px] text-slate-400">UPLOAD</div>
                            <div class="text-xl font-black text-violet-300"><span id="speed-upload">—</span><span class="text-xs font-semibold ml-1">Mbps</span></div>
                            <div id="speed-upload-status" class="text-[9px] text-slate-500">Menunggu tes</div>
                        </div>
                        <div class="bg-slate-950 border border-slate-800 rounded-xl p-3">
                            <div class="text-[10px] text-slate-400">LATENCY</div>
                            <div class="text-xl font-black text-emerald-300"><span id="speed-latency">—</span><span class="text-xs font-semibold ml-1">ms</span></div>
                            <div class="text-[9px] text-slate-500">Rata-rata latency</div>
                        </div>
                        <div class="bg-slate-950 border border-slate-800 rounded-xl p-3">
                            <div class="text-[10px] text-slate-400">STATUS</div>
                            <div id="speed-state" class="text-sm font-bold text-slate-300">Siap</div>
                            <div id="speed-elapsed" class="text-[9px] text-slate-500">Belum berjalan</div>
                        </div>
                    </div>

                    <div class="bg-slate-950/80 border border-slate-800 rounded-xl p-3">
                        <div class="flex items-center justify-between mb-2">
                            <span class="text-[11px] font-semibold text-slate-300">Progres Pengujian</span>
                            <span id="speed-progress-label" class="text-[10px] text-cyan-300">0%</span>
                        </div>
                        <div class="h-2 rounded-full bg-slate-800 overflow-hidden">
                            <div id="speed-progress" class="h-full w-0 rounded-full bg-gradient-to-r from-cyan-500 via-blue-500 to-violet-500 transition-all duration-500"></div>
                        </div>
                        <p id="speed-message" class="text-[10px] text-slate-400 mt-2">Tekan tombol untuk memulai pengujian. Tes menggunakan server Cloudflare.</p>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div class="bg-slate-950/70 border border-slate-800 rounded-xl p-3">
                            <div class="text-[11px] font-bold text-slate-300 mb-2">Statistik Download (Mbps)</div>
                            <div class="grid grid-cols-3 gap-2 text-center">
                                <div><div class="text-[9px] text-slate-500">MIN</div><div id="speed-dl-min" class="text-sm font-bold text-cyan-300">—</div></div>
                                <div><div class="text-[9px] text-slate-500">RATA-RATA</div><div id="speed-dl-avg" class="text-sm font-bold text-cyan-300">—</div></div>
                                <div><div class="text-[9px] text-slate-500">MAKS</div><div id="speed-dl-max" class="text-sm font-bold text-cyan-300">—</div></div>
                            </div>
                        </div>
                        <div class="bg-slate-950/70 border border-slate-800 rounded-xl p-3">
                            <div class="text-[11px] font-bold text-slate-300 mb-2">Statistik Upload (Mbps)</div>
                            <div class="grid grid-cols-3 gap-2 text-center">
                                <div><div class="text-[9px] text-slate-500">MIN</div><div id="speed-ul-min" class="text-sm font-bold text-violet-300">—</div></div>
                                <div><div class="text-[9px] text-slate-500">RATA-RATA</div><div id="speed-ul-avg" class="text-sm font-bold text-violet-300">—</div></div>
                                <div><div class="text-[9px] text-slate-500">MAKS</div><div id="speed-ul-max" class="text-sm font-bold text-violet-300">—</div></div>
                            </div>
                        </div>
                    </div>

                    <div class="bg-slate-950/70 border border-slate-800 rounded-xl p-3">
                        <div class="text-[11px] font-bold text-slate-300 mb-2">Statistik Latensi (ms)</div>
                        <div class="grid grid-cols-3 gap-2 text-center">
                            <div><div class="text-[9px] text-slate-500">MIN</div><div id="speed-lat-min" class="text-sm font-bold text-emerald-300">—</div></div>
                            <div><div class="text-[9px] text-slate-500">RATA-RATA</div><div id="speed-lat-avg" class="text-sm font-bold text-emerald-300">—</div></div>
                            <div><div class="text-[9px] text-slate-500">MAKS</div><div id="speed-lat-max" class="text-sm font-bold text-emerald-300">—</div></div>
                        </div>
                    </div>

                    <div class="bg-slate-950/70 border border-slate-800 rounded-xl p-3">
                        <div class="text-[11px] font-bold text-slate-300 mb-2">Grafik Real-time (Mbps / ms)</div>
                        <div class="h-44"><canvas id="speedChart"></canvas></div>
                    </div>
                </div>

                <!-- Tab 4: About & Update Details -->
                <div id="tab-about" class="tab-pane absolute inset-0 w-full overflow-y-auto overscroll-contain space-y-3 pt-1 pr-1 opacity-0 scale-[0.985] translate-y-1 pointer-events-none hidden">
                    <div class="rounded-xl border border-cyan-900/70 bg-cyan-950/20 p-4">
                        <div class="text-lg font-black tracking-wide text-cyan-300">IRA ZTE MC8501 5G LIVE SIGNAL CHARTS</div>
                        <div class="text-[11px] text-slate-400 mt-1">Versi aplikasi: <span id="about-app-version" class="text-slate-200 font-semibold">__APP_VERSION__</span></div>
                        <p class="text-[11px] text-slate-300 mt-3 leading-relaxed">Dashboard desktop untuk memantau parameter sinyal 5G router ZTE MC8501 secara real-time, melihat status tower dan internet, memeriksa latensi, serta menjalankan tes kecepatan jaringan.</p>
                    </div>
                    <div class="rounded-xl border border-slate-800 bg-slate-950/50 p-3 space-y-2">
                        <div class="text-[11px] font-bold text-cyan-300">Sumber & Teknologi</div>
                        <div class="text-[10px] text-slate-300 leading-relaxed">• Kode sumber dan rilis aplikasi: GitHub <b>TheKingTermux/ira-zte-live-signal-charts</b><br>• Data sinyal: endpoint lokal router ZTE MC8501 (<code>zte_nwinfo_api / nwinfo_get_netinfo</code>)<br>• Grafik: Chart.js<br>• Tampilan: Tailwind CSS<br>• Aplikasi desktop: Python + pywebview<br>• Tes download/upload: endpoint publik Cloudflare Speed Test</div>
                        <div class="flex flex-wrap gap-2 pt-1">
                            <button onclick="openExternalUrl('https://github.com/TheKingTermux/ira-zte-live-signal-charts')" class="bg-slate-800 hover:bg-slate-700 text-slate-200 text-[10px] font-semibold px-3 py-2 rounded-lg">↗ Repositori GitHub</button>
                            <button onclick="openExternalUrl('https://github.com/TheKingTermux/ira-zte-live-signal-charts/releases')" class="bg-slate-800 hover:bg-slate-700 text-slate-200 text-[10px] font-semibold px-3 py-2 rounded-lg">↗ Semua Release</button>
                        </div>
                    </div>
                    <div class="rounded-xl border border-slate-800 bg-slate-950/50 p-3 space-y-3">
                        <div class="text-[11px] font-bold text-cyan-300">Pembaruan Aplikasi</div>
                        <p class="text-[10px] text-slate-400">Pilih kanal Stable untuk rilis reguler atau Beta untuk versi pre-release. Jika pemasangan otomatis aktif, update yang cocok akan diunduh dan dipasang saat aplikasi dibuka. Pengaturan kanal dan pemasangan otomatis tersedia di sini.</p>
                        <div>
                            <label class="text-[10px] text-slate-400 block mb-1">Saluran rilis</label>
                            <select id="setting-update-channel" onchange="saveUpdatePreferences(); checkForUpdates(true)" class="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 p-2 rounded-xl focus:outline-none focus:border-cyan-500">
                                <option value="stable">Stable — rilis resmi</option>
                                <option value="beta">Beta — pre-release</option>
                            </select>
                        </div>
                        <label class="flex items-center gap-2 text-[11px] text-slate-300">
                            <input id="setting-auto-update-check" type="checkbox" onchange="saveUpdatePreferences()" class="accent-cyan-500">
                            Periksa dan pasang update otomatis saat aplikasi dibuka
                        </label>
                        <div class="flex flex-col sm:flex-row gap-2">
                            <button id="btn-check-update" onclick="checkForUpdates(false)" class="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-[10px] font-semibold px-3 py-2 rounded-lg">🔎 Periksa Update</button>
                            <button id="btn-install-update" onclick="installAvailableUpdate()" disabled class="flex-1 bg-cyan-700 hover:bg-cyan-600 disabled:opacity-40 disabled:cursor-not-allowed text-white text-[10px] font-semibold px-3 py-2 rounded-lg">⬇ Unduh & Pasang</button>
                        </div>
                        <p id="update-status" class="text-[10px] text-slate-400">Belum memeriksa update.</p>
                        <div id="update-progress-panel" class="hidden space-y-1.5 rounded-lg border border-slate-800 bg-slate-950/70 p-2">
                            <div class="flex justify-between gap-2 text-[10px]"><span id="update-progress-label">Menyiapkan unduhan…</span><span id="update-progress-percent">0%</span></div>
                            <div class="h-2 overflow-hidden rounded-full bg-slate-800"><div id="update-progress-bar" class="h-full w-0 rounded-full bg-cyan-500 transition-[width] duration-200"></div></div>
                            <div id="update-progress-details" class="text-[10px] text-slate-400">Menghitung ukuran, kecepatan, dan sisa waktu…</div>
                        </div>
                        <div class="border-t border-slate-800 pt-3">
                            <div class="text-[11px] font-bold text-cyan-300 mb-1">Informasi Release</div>
                            <p id="about-update-details" class="text-[10px] text-slate-400">Belum ada informasi release.</p>
                        </div>
                    </div>
                </div>
            </div>

            <div class="pt-3 flex justify-end border-t border-slate-800 mt-3 shrink-0 bg-slate-900">
                <button onclick="animateButton(this); toggleSettingsModal()" class="w-full bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold py-2.5 rounded-xl shadow-lg transition-all active:scale-95">Tutup</button>
            </div>
        </div>
    </div>

    <!-- Disconnected Alert Popup Modal (Animated with Recheck Button) -->
    <div id="disconnectModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm opacity-0 pointer-events-none modal-transition">
        <div id="disconnectBox" class="bg-slate-900 border-2 border-orange-500/80 p-6 rounded-2xl max-w-md w-full mx-4 shadow-2xl shadow-orange-500/20 text-slate-100 transform scale-95 transition-transform duration-250">
            <div class="w-12 h-12 bg-orange-500/10 text-orange-500 rounded-xl flex items-center justify-center mx-auto mb-3 text-2xl font-bold animate-bounce">⚠️</div>
            <h3 id="modal-title-disc" class="text-lg font-bold text-orange-400 text-center mb-1">KONEKSI TOWER TERPUTUS!</h3>
            <p id="modal-desc-disc" class="text-xs text-slate-300 text-center mb-4">Sinyal bar terdeteksi 0 atau terputus dari jaringan utama.</p>
            <div class="space-y-2">
                <button onclick="animateButton(this); manualReconnectCheck()" id="btn-recheck" class="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-2.5 px-4 rounded-xl text-xs shadow-lg transition-all active:scale-95">🔄 Uji Ulang Koneksi Internet</button>
                <button onclick="animateButton(this); closeDisconnectModal()" class="w-full bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold py-2 px-4 rounded-xl text-xs transition-all active:scale-95">Tutup Peringatan</button>
            </div>
        </div>
    </div>

    <!-- Reconnected Alert Popup Modal (Animated) -->
    <div id="reconnectModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm opacity-0 pointer-events-none modal-transition">
        <div id="reconnectBox" class="bg-slate-900 border-2 border-emerald-500/80 p-6 rounded-2xl max-w-md w-full mx-4 shadow-2xl shadow-emerald-500/20 text-slate-100 transform scale-95 transition-transform duration-250">
            <div class="w-12 h-12 bg-emerald-500/10 text-emerald-500 rounded-xl flex items-center justify-center mx-auto mb-3 text-2xl font-bold animate-bounce">✅</div>
            <h3 class="text-lg font-bold text-emerald-400 text-center mb-1">KONEKSI KEMBALI NORMAL!</h3>
            <p class="text-xs text-slate-300 text-center mb-4">Tower dan akses internet berhasil tersambung kembali dengan lancar dan stabil.</p>
            <button onclick="animateButton(this); closeReconnectModal()" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-2.5 px-4 rounded-xl text-xs shadow-lg transition-all active:scale-95">Tutup Peringatan</button>
        </div>
    </div>

    <!-- History Log Modal (Animated) -->
    <div id="historyModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm opacity-0 pointer-events-none modal-transition">
        <div id="historyBox" class="bg-slate-900 border border-slate-800 p-5 rounded-2xl max-w-lg w-full mx-4 shadow-2xl max-h-[80vh] flex flex-col text-slate-100 transform scale-95 transition-transform duration-250">
            <div class="flex justify-between items-center mb-3 pb-2 border-b border-slate-800">
                <h3 class="text-sm font-bold text-cyan-400 flex items-center gap-2">🔔 Riwayat Jaringan & Pemutusan</h3>
                <button onclick="animateButton(this); toggleHistoryModal()" class="text-slate-400 hover:text-white text-xs font-bold px-2 py-1 rounded-lg bg-slate-800">✕</button>
            </div>
            <div id="history-list" class="overflow-y-auto space-y-2 flex-grow pr-1 text-xs">
                <div class="text-center text-slate-500 py-6">Belum ada riwayat tercatat dalam sesi ini.</div>
            </div>
            <div class="mt-3 pt-2 border-t border-slate-800 flex justify-end">
                <button onclick="animateButton(this); clearHistory()" class="text-[11px] bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-1.5 rounded-lg transition-all active:scale-95">Bersihkan Riwayat</button>
            </div>
        </div>
    </div>

    <script>
        Chart.defaults.color = '#64748b';
        Chart.defaults.font.family = 'ui-sans-serif, system-ui, sans-serif';

        const maxDataPoints = 30;
        let connectionHistory = [];
        // Connection state is debounced so a single timeout does not cause alert/recovery flapping.
        let wasConnected = null;
        let wasInternetOk = null;
        let towerFailCount = 0;
        let towerSuccessCount = 0;
        let internetFailCount = 0;
        let internetSuccessCount = 0;
        let towerIssueNotified = false;
        let internetIssueNotified = false;
        let noticeTimer = null;
        let unreadCount = 0;
        let currentIntervalTime = 1000;
        let pollTimer = null;

        window.addEventListener('DOMContentLoaded', () => {
            loadSettings();
            requestAnimationFrame(() => resizeSettingsContent('tab-general', false));
        });

        window.addEventListener('pywebviewready', function() {
            const pingFreqSelect = document.getElementById('setting-ping-freq');
            const savedPingFreq = localStorage.getItem('router_ping_freq');
            if (savedPingFreq === null || savedPingFreq === 'auto') {
                pingFreqSelect.value = 'auto';
                updatePingMonitorFrequency(false);
            } else {
                const savedInterval = Number.parseInt(savedPingFreq, 10);
                if (Number.isFinite(savedInterval) && savedInterval >= 1000 && savedInterval <= 3600000) {
                    pingFreqSelect.value = 'custom';
                    pingMonitorInterval = savedInterval;
                    const customInput = document.getElementById('setting-ping-freq-custom');
                    customInput.classList.remove('hidden');
                    customInput.value = String(Math.round(savedInterval / 1000));
                    const pingTitle = document.getElementById('ping-chart-title');
                    if (pingTitle) pingTitle.textContent = '📈 Ping Latency — setiap ' + (pingMonitorInterval / 1000) + ' detik';
                } else {
                    pingFreqSelect.value = 'auto';
                    localStorage.setItem('router_ping_freq', 'auto');
                    updatePingMonitorFrequency(false);
                }
            }
            startPolling();
            startPingMonitor();
        });

        // Loop polling: tiap siklus membaca currentIntervalTime TERBARU.
        // try/finally memastikan loop tidak pernah berhenti walau ada error.
        let pollGeneration = 0;

        function startPolling() {
            pollGeneration++;
            const myGen = pollGeneration;
            if (pollTimer) { clearTimeout(pollTimer); pollTimer = null; }

            const tick = async () => {
                if (myGen !== pollGeneration) return;
                const started = Date.now();
                try {
                    await fetchTelemetry();
                } catch (e) {
                    console.error('Polling error:', e);
                } finally {
                    if (myGen === pollGeneration) {
                        const wait = Math.max(0, currentIntervalTime - (Date.now() - started));
                        pollTimer = setTimeout(tick, wait);
                    }
                }
            };
            tick();
        }

        // Web Audio API Disconnect Chime (3 nada menurun, bernuansa lonceng)
        let sharedAudioCtx = null;

        function getAudioCtx() {
            if (!sharedAudioCtx) {
                const Ctx = window.AudioContext || window.webkitAudioContext;
                if (Ctx) sharedAudioCtx = new Ctx();
            }
            return sharedAudioCtx;
        }

        // Browser/webview kadang memblokir audio sebelum ada interaksi pertama
        ['pointerdown', 'keydown'].forEach(evt => {
            window.addEventListener(evt, () => {
                const ctx = getAudioCtx();
                if (ctx && ctx.state === 'suspended') ctx.resume();
            }, { once: true });
        });

        function playAlertSound() {
            try {
                const ctx = getAudioCtx();
                if (!ctx) return;
                if (ctx.state === 'suspended') ctx.resume();

                // A5 -> E5 -> C#5 (menurun, terdengar sebagai peringatan)
                const notes = [880.00, 659.25, 554.37];
                const step = 0.28;      // jeda antar nada (detik)
                const decay = 1.1;      // lama gema tiap nada (detik)
                const t0 = ctx.currentTime + 0.02;

                notes.forEach((freq, i) => {
                    const t = t0 + i * step;

                    const master = ctx.createGain();
                    master.gain.setValueAtTime(0.0001, t);
                    master.gain.exponentialRampToValueAtTime(0.3, t + 0.015);
                    master.gain.exponentialRampToValueAtTime(0.0001, t + decay);
                    master.connect(ctx.destination);

                    // Nada dasar + overtone 2x (lebih lemah) untuk karakter lonceng
                    [[freq, 1.0], [freq * 2, 0.35]].forEach(([f, level]) => {
                        const osc = ctx.createOscillator();
                        const g = ctx.createGain();
                        osc.type = 'sine';
                        osc.frequency.setValueAtTime(f, t);
                        g.gain.setValueAtTime(level, t);
                        osc.connect(g);
                        g.connect(master);
                        osc.start(t);
                        osc.stop(t + decay + 0.05);
                    });
                });
            } catch (e) {
                console.log("Audio alert suppressed:", e);
            }
        }

        // Smooth settings tabs with content-driven modal height.
        let activeSettingsTab = 'tab-general';
        let settingsTabTimers = new Map();

        function resizeSettingsContent(tabId = activeSettingsTab, animate = true) {
            const content = document.getElementById('settingsContent');
            const pane = document.getElementById(tabId);
            if (!content || !pane) return;

            // Measure the full content, then cap it to the space available in the viewport.
            const maxHeight = Math.max(150, Math.min(window.innerHeight * 0.92 - 190, window.innerHeight * 0.92 - 130));
            const naturalHeight = Math.max(pane.scrollHeight, pane.offsetHeight);
            const targetHeight = Math.min(naturalHeight, maxHeight);
            if (!animate) content.style.transition = 'none';
            content.style.height = `${targetHeight}px`;
            if (!animate) {
                void content.offsetHeight;
                content.style.removeProperty('transition');
            }
            pane.style.overflowY = naturalHeight > targetHeight ? 'auto' : 'hidden';
        }

        function switchTab(tabId) {
            const allTabs = ['tab-general', 'tab-ping', 'tab-speed', 'tab-about'];
            if (!allTabs.includes(tabId) || tabId === activeSettingsTab) return;

            const previousTab = activeSettingsTab;
            activeSettingsTab = tabId;
            const previousPane = document.getElementById(previousTab);
            const nextPane = document.getElementById(tabId);

            for (const [id, timer] of settingsTabTimers) {
                clearTimeout(timer);
                settingsTabTimers.delete(id);
            }

            allTabs.forEach(id => {
                const pane = document.getElementById(id);
                if (id !== previousTab && id !== tabId) pane.classList.add('hidden');
            });

            nextPane.classList.remove('hidden');
            nextPane.classList.add('opacity-0', 'scale-[0.985]', 'translate-y-1', 'pointer-events-none');
            nextPane.classList.remove('opacity-100', 'scale-100', 'translate-y-0', 'pointer-events-auto');

            // Resize the wrapper to this tab's own content; its height animates instead of jumping.
            resizeSettingsContent(tabId, true);

            previousPane.classList.remove('opacity-100', 'scale-100', 'translate-y-0', 'pointer-events-auto');
            previousPane.classList.add('opacity-0', 'scale-[0.985]', 'translate-y-1', 'pointer-events-none');

            void nextPane.offsetWidth;
            requestAnimationFrame(() => {
                if (activeSettingsTab !== tabId) return;
                nextPane.classList.remove('opacity-0', 'scale-[0.985]', 'translate-y-1', 'pointer-events-none');
                nextPane.classList.add('opacity-100', 'scale-100', 'translate-y-0', 'pointer-events-auto');
            });

            const timer = setTimeout(() => {
                if (activeSettingsTab !== previousTab) previousPane.classList.add('hidden');
                settingsTabTimers.delete(previousTab);
            }, 250);
            settingsTabTimers.set(previousTab, timer);

            ['general', 'ping', 'speed', 'about'].forEach(name => {
                const btn = document.getElementById('btn-tab-' + name);
                const selected = 'tab-' + name === tabId;
                btn.className = selected
                    ? 'flex-1 py-2 font-semibold text-cyan-400 border-b-2 border-cyan-400 bg-cyan-500/10 transition-all duration-300'
                    : 'flex-1 py-2 font-semibold text-slate-400 border-b-2 border-transparent hover:text-slate-200 transition-all duration-300';
                btn.setAttribute('aria-selected', selected ? 'true' : 'false');
            });
        }

        window.addEventListener('resize', () => resizeSettingsContent(activeSettingsTab, false));

        // Manual Reconnect Check Button Handler
        async function manualReconnectCheck() {
            let btn = document.getElementById('btn-recheck');
            btn.disabled = true;
            btn.innerText = "⏳ Sedang Menguji...";
            
            await fetchTelemetry();
            
            setTimeout(() => {
                btn.disabled = false;
                btn.innerText = "🔄 Uji Ulang Koneksi Internet";
            }, 800);
        }

        function toggleAccordion() {
            let content = document.getElementById('accordion-content');
            let arrow = document.getElementById('accordion-arrow');
            if (content.classList.contains('open')) {
                content.classList.remove('open');
                arrow.style.transform = 'rotate(0deg)';
            } else {
                content.classList.add('open');
                arrow.style.transform = 'rotate(180deg)';
            }
        }

        async function runPing(btn) {
            const input = document.getElementById('ping-host');
            const host = input.value.trim();
            const outputEl = document.getElementById('ping-output');

            // Client-side validation is for usability; Python validates again securely.
            const hostnamePattern = /^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)(?:\\.(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?))*$/;
            const isIPv4 = /^(?:(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)\\.){3}(?:25[0-5]|2[0-4]\\d|1\\d\\d|[1-9]?\\d)$/.test(host);
            const isIPv6Like = /^[0-9a-fA-F:]+$/.test(host) && host.includes(':');
            if (!host || host.length > 253 || host.startsWith('-') || !(isIPv4 || isIPv6Like || hostnamePattern.test(host))) {
                outputEl.innerText = 'Host/IP tidak valid. Masukkan alamat IP atau nama host yang valid (maksimal 253 karakter).';
                return;
            }
            if (!window.pywebview || !window.pywebview.api) {
                outputEl.innerText = 'API aplikasi belum siap.';
                return;
            }

            btn.disabled = true;
            btn.innerText = 'Pinging...';
            outputEl.classList.add('animate-pulse');
            outputEl.innerText = `Mengirim paket ping ke ${host}...\n`;

            try {
                let result = await window.pywebview.api.run_ping(host);
                outputEl.classList.remove('animate-pulse');
                if (result.success) {
                    outputEl.innerText = result.output;
                } else {
                    outputEl.innerText = `Error: ${result.output}`;
                }
            } catch (e) {
                outputEl.classList.remove('animate-pulse');
                outputEl.innerText = `Gagal menjalankan ping: ${e}`;
            }
            btn.disabled = false;
            btn.innerText = 'Ping';
        }

        let speedChartInstance = null;
        let speedTestRunning = false;
        const SPEED_PHASE_SECONDS = 30;

        function setSpeedProgress(percent, message) {
            const value = Math.max(0, Math.min(100, percent));
            document.getElementById('speed-progress').style.width = value + '%';
            document.getElementById('speed-progress-label').innerText = Math.round(value) + '%';
            if (message) document.getElementById('speed-message').innerText = message;
        }

        function animateNumber(id, target, decimals = 2, duration = 900) {
            const el = document.getElementById(id);
            const end = Number(target);
            if (!Number.isFinite(end)) { el.innerText = '—'; return; }
            const start = Number.parseFloat(el.innerText.replace(/[^0-9.-]/g, '')) || 0;
            const began = performance.now();
            function frame(now) {
                const t = Math.min(1, (now - began) / duration);
                const eased = 1 - Math.pow(1 - t, 3);
                el.innerText = (start + (end - start) * eased).toFixed(decimals);
                if (t < 1) requestAnimationFrame(frame);
            }
            requestAnimationFrame(frame);
        }

        const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

        function getStats(values, decimals = 2) {
            if (!values.length) return { min: null, max: null, avg: null, samples: [] };
            return {
                min: Number(Math.min(...values).toFixed(decimals)),
                max: Number(Math.max(...values).toFixed(decimals)),
                avg: Number((values.reduce((a, b) => a + b, 0) / values.length).toFixed(decimals)),
                samples: values.slice()
            };
        }

        function initSpeedChart() {
            if (speedChartInstance) speedChartInstance.destroy();
            speedChartInstance = new Chart(document.getElementById('speedChart').getContext('2d'), {
                type: 'line',
                data: { labels: [], datasets: [
                    { label: 'Download (Mbps)', data: [], borderColor: '#22d3ee', backgroundColor: 'rgba(34,211,238,0.10)', fill: true, tension: 0.25, pointRadius: 0, pointHoverRadius: 4, borderWidth: 2, spanGaps: false, yAxisID: 'ySpeed' },
                    { label: 'Upload (Mbps)', data: [], borderColor: '#a78bfa', backgroundColor: 'rgba(167,139,250,0.08)', fill: true, tension: 0.25, pointRadius: 0, pointHoverRadius: 4, borderWidth: 2, spanGaps: false, yAxisID: 'ySpeed' },
                    { label: 'Latency (ms)', data: [], borderColor: '#34d399', backgroundColor: 'rgba(52,211,153,0.06)', fill: false, tension: 0.25, pointRadius: 0, pointHoverRadius: 4, borderWidth: 2, spanGaps: false, yAxisID: 'yLatency' }
                ]},
                options: {
                    responsive: true, maintainAspectRatio: false,
                    animation: { duration: 180, easing: 'easeOutQuad' },
                    interaction: { intersect: false, mode: 'index' },
                    plugins: { legend: { labels: { color: '#cbd5e1', boxWidth: 10, font: { size: 10 } } } },
                    scales: {
                        x: { ticks: { color: '#94a3b8', font: { size: 9 }, maxTicksLimit: 10 }, grid: { color: 'rgba(148,163,184,0.08)' }, title: { display: true, text: 'Waktu (detik)', color: '#94a3b8' } },
                        ySpeed: { type: 'linear', position: 'left', beginAtZero: true, ticks: { color: '#22d3ee', font: { size: 9 } }, grid: { color: 'rgba(148,163,184,0.10)' }, title: { display: true, text: 'Mbps', color: '#22d3ee' } },
                        yLatency: { type: 'linear', position: 'right', beginAtZero: true, ticks: { color: '#34d399', font: { size: 9 } }, grid: { drawOnChartArea: false }, title: { display: true, text: 'ms', color: '#34d399' } }
                    }
                }
            });
        }

        function appendSpeedSample(elapsedSeconds, phase, value) {
            if (!speedChartInstance) return;
            const label = elapsedSeconds.toFixed(0);
            const datasets = speedChartInstance.data.datasets;
            speedChartInstance.data.labels.push(label);
            datasets.forEach((dataset, index) => dataset.data.push(index === phase ? value : null));
            // Fixed, monotonically increasing X labels + no shifting avoids the old edge-point artifact.
            speedChartInstance.update('none');
        }

        async function runSpeedTest() {
            if (speedTestRunning) return;
            if (!window.pywebview || !window.pywebview.api || typeof window.pywebview.api.run_speed_sample !== 'function') {
                document.getElementById('speed-state').innerText = 'API tidak tersedia';
                document.getElementById('speed-message').innerText = 'API speed test belum siap. Tunggu aplikasi selesai dimuat, lalu coba lagi.';
                return;
            }

            speedTestRunning = true;
            const btn = document.getElementById('btn-speed-test');
            const started = performance.now();
            const values = { download: [], upload: [], latency: [] };
            const failures = { download: 0, upload: 0, latency: 0 };
            const phases = [
                { key: 'download', label: 'Download', dataset: 0, unit: 'Mbps', statusId: 'speed-download-status' },
                { key: 'upload', label: 'Upload', dataset: 1, unit: 'Mbps', statusId: 'speed-upload-status' },
                { key: 'latency', label: 'Latensi', dataset: 2, unit: 'ms', statusId: 'speed-latency-status' }
            ];
            btn.disabled = true;
            btn.innerText = '⏳ Tes download → upload → latensi…';
            document.getElementById('speed-state').innerText = 'Menghubungkan ke server speed test…';
            document.getElementById('speed-message').innerText =
                'Tes akan dimulai setelah server Cloudflare merespons. Setiap sampel memiliki batas waktu dan error akan ditampilkan di sini.';
            document.getElementById('speed-state').className = 'text-sm font-bold text-cyan-300';
            document.getElementById('speed-elapsed').innerText = '0.0 / 90 detik';
            ['speed-download','speed-upload','speed-latency','speed-dl-min','speed-dl-avg','speed-dl-max','speed-ul-min','speed-ul-avg','speed-ul-max','speed-lat-min','speed-lat-avg','speed-lat-max'].forEach(id => document.getElementById(id).innerText = '—');
            document.getElementById('speed-download-status').innerText = 'Menunggu giliran';
            document.getElementById('speed-upload-status').innerText = 'Menunggu giliran';
            document.getElementById('speed-latency-status').innerText = 'Menunggu giliran';
            initSpeedChart();

            const elapsedTimer = setInterval(() => {
                const elapsed = (performance.now() - started) / 1000;
                document.getElementById('speed-elapsed').innerText = elapsed.toFixed(1) + ' / 90 detik';
            }, 100);

            try {
                for (let phaseIndex = 0; phaseIndex < phases.length; phaseIndex++) {
                    const phase = phases[phaseIndex];
                    const phaseStarted = performance.now();
                    document.getElementById('speed-state').innerText = phase.label + ' berlangsung';
                    document.getElementById(phase.statusId).innerText = 'Memulai pengukuran 30 detik…';
                    setSpeedProgress((phaseIndex / 3) * 100, `Fase ${phaseIndex + 1}/3: ${phase.label} · 30 detik`);
                    let nextSampleAt = phaseStarted;

                    while ((performance.now() - phaseStarted) < SPEED_PHASE_SECONDS * 1000) {
                        const callStarted = performance.now();
                        const remainingPhase = SPEED_PHASE_SECONDS * 1000 - (callStarted - phaseStarted);
                        try {
                            document.getElementById(phase.statusId).innerText =
                                `Menghubungi server untuk ${phase.label.toLowerCase()}…`;
                            document.getElementById('speed-state').innerText =
                                `${phase.label}: mengukur sampel ${values[phase.key].length + 1}`;
                            // Python requests have explicit connect/read timeouts. Avoid Promise.race here:
                            // abandoning the JS promise would leave the underlying network request running.
                            const result = await window.pywebview.api.run_speed_sample(phase.key);
                            if (!result || !result.success || !Number.isFinite(Number(result.value))) {
                                throw new Error((result && result.error) || 'Hasil sampel tidak valid');
                            }
                            const value = Number(result.value);
                            values[phase.key].push(value);
                            appendSpeedSample((performance.now() - started) / 1000, phase.dataset, value);
                            const stats = getStats(values[phase.key], phase.key === 'latency' ? 1 : 2);
                            const mainId = phase.key === 'download' ? 'speed-download' : phase.key === 'upload' ? 'speed-upload' : 'speed-latency';
                            animateNumber(mainId, stats.avg, phase.key === 'latency' ? 1 : 2, 220);
                            document.getElementById(phase.statusId).innerText = `${values[phase.key].length} sampel · ${failures[phase.key]} gagal`;
                            setSpeedProgress(((phaseIndex * SPEED_PHASE_SECONDS + Math.min(SPEED_PHASE_SECONDS, (performance.now() - phaseStarted) / 1000)) / 90) * 100,
                                `${phase.label}: ${value.toFixed(phase.key === 'latency' ? 1 : 2)} ${phase.unit} · ${values[phase.key].length} sampel`);
                        } catch (sampleError) {
                            failures[phase.key]++;
                            document.getElementById(phase.statusId).innerText = `Gagal ${failures[phase.key]}x · mencoba lagi`;
                            document.getElementById('speed-message').innerText =
                                `${phase.label}: ${sampleError.message || sampleError}. Pastikan internet aktif dan akses ke speed.cloudflare.com tidak diblokir.`;
                        }
                        nextSampleAt = Math.max(nextSampleAt + 1000, callStarted + 1000);
                        const remaining = Math.min(nextSampleAt - performance.now(), remainingPhase);
                        if (remaining > 0 && (performance.now() - phaseStarted) < SPEED_PHASE_SECONDS * 1000) await sleep(remaining);
                    }
                    // Update phase status immediately; don't leave the UI in a "preparing" state.
                    document.getElementById('speed-state').innerText = phaseIndex < 2 ? `Menyiapkan ${phases[phaseIndex + 1].label.toLowerCase()}` : 'Menyelesaikan hasil';
                }

                const dl = getStats(values.download, 2);
                const ul = getStats(values.upload, 2);
                const lat = getStats(values.latency, 1);
                if (!dl.samples.length || !ul.samples.length || !lat.samples.length) {
                    throw new Error('Tidak ada sampel yang berhasil untuk salah satu fase. Periksa koneksi internet dan coba lagi.');
                }
                for (const [id, stats, decimals] of [
                    ['speed-download', dl, 2], ['speed-upload', ul, 2], ['speed-latency', lat, 1]
                ]) animateNumber(id, stats.avg, decimals, 650);
                for (const [prefix, stats] of [['speed-dl', dl], ['speed-ul', ul], ['speed-lat', lat]]) {
                    const decimals = prefix === 'speed-lat' ? 1 : 2;
                    animateNumber(prefix + '-min', stats.min, decimals, 650);
                    animateNumber(prefix + '-avg', stats.avg, decimals, 650);
                    animateNumber(prefix + '-max', stats.max, decimals, 650);
                }
                document.getElementById('speed-download-status').innerText = `${dl.samples.length} sampel selesai · ${failures.download} gagal`;
                document.getElementById('speed-upload-status').innerText = `${ul.samples.length} sampel selesai · ${failures.upload} gagal`;
                document.getElementById('speed-latency-status').innerText = `${lat.samples.length} sampel selesai · ${failures.latency} gagal`;
                document.getElementById('speed-state').innerText = 'Selesai';
                document.getElementById('speed-state').className = 'text-sm font-bold text-emerald-400';
                setSpeedProgress(100, 'Selesai: download 30 dtk → upload 30 dtk → latensi 30 dtk.');
            } catch (error) {
                document.getElementById('speed-state').innerText = 'Gagal';
                document.getElementById('speed-state').className = 'text-sm font-bold text-red-400';
                setSpeedProgress(100, 'Pengujian dihentikan: ' + (error.message || error));
            } finally {
                clearInterval(elapsedTimer);
                speedTestRunning = false;
                btn.disabled = false;
                btn.innerText = '▶ Ulangi Speed Test';
            }
        }

        function animateButton(btn) {
            btn.style.transform = 'scale(0.9)';
            setTimeout(() => btn.style.transform = 'scale(1)', 150);
        }

        function loadSettings() {
            const savedTheme = localStorage.getItem('router_theme') || 'dark';
            const allowedFrequencies = ['1000', '2000', '4000'];
            const storedFreq = localStorage.getItem('router_freq') || '1000';
            const savedFreq = allowedFrequencies.includes(storedFreq) ? storedFreq : '1000';

            document.getElementById('setting-theme').value = savedTheme;
            changeTheme(savedTheme, false);
            document.getElementById('setting-freq').value = savedFreq;
            currentIntervalTime = Number.parseInt(savedFreq, 10);
            document.getElementById('suppress-tower-popup').checked = localStorage.getItem('suppress_tower_popup') === 'true';
            document.getElementById('suppress-internet-popup').checked = localStorage.getItem('suppress_internet_popup') === 'true';
            const updateChannel = localStorage.getItem('update_channel') === 'beta' ? 'beta' : 'stable';
            document.getElementById('setting-update-channel').value = updateChannel;
            document.getElementById('setting-auto-update-check').checked = localStorage.getItem('auto_update_check') !== 'false';
            document.getElementById('about-app-version').innerText = APP_VERSION_JS;
            if (document.getElementById('setting-auto-update-check').checked) {
                setTimeout(() => checkForUpdates(true), 1800);
            }
        }

        const APP_VERSION_JS = "__APP_VERSION__";
        let availableUpdate = null;
        let updateInstallInProgress = false;

        function saveUpdatePreferences() {
            localStorage.setItem('update_channel', document.getElementById('setting-update-channel').value);
            localStorage.setItem('auto_update_check', String(document.getElementById('setting-auto-update-check').checked));
        }

        function setUpdateStatus(message, isError = false) {
            const el = document.getElementById('update-status');
            el.innerText = message;
            el.className = 'text-[10px] ' + (isError ? 'text-orange-300' : 'text-slate-400');
        }

        async function checkForUpdates(silent = false) {
            const btn = document.getElementById('btn-check-update');
            const installBtn = document.getElementById('btn-install-update');
            const channel = document.getElementById('setting-update-channel').value;
            if (!window.pywebview || !window.pywebview.api || typeof window.pywebview.api.check_for_updates !== 'function') {
                setUpdateStatus('API updater belum siap.');
                return;
            }
            if (btn) { btn.disabled = true; btn.innerText = 'Memeriksa…'; }
            if (!silent) setUpdateStatus('Menghubungi GitHub untuk memeriksa release…');
            try {
                const result = await window.pywebview.api.check_for_updates(channel);
                availableUpdate = result && result.update_available ? result : null;
                if (availableUpdate) {
                    const versionText = `${result.name || result.tag_name} (${channel === 'beta' ? 'Beta' : 'Stable'})`;
                    setUpdateStatus(`Update tersedia: ${versionText}. Klik Unduh & Pasang untuk menerapkan.`);
                    document.getElementById('about-update-details').innerText = `Tersedia ${versionText}. ${result.published_at ? 'Dipublikasikan: ' + result.published_at : ''}`;
                    installBtn.disabled = false;
                    if (silent && document.getElementById('setting-auto-update-check').checked && !updateInstallInProgress) {
                        setUpdateStatus(`Update ${versionText} ditemukan. Memasang otomatis…`);
                        setTimeout(() => installAvailableUpdate(), 600);
                    }
                } else if (result && result.error) {
                    setUpdateStatus(result.error, true);
                    document.getElementById('about-update-details').innerText = result.error;
                    installBtn.disabled = true;
                } else {
                    const msg = result && result.message ? result.message : 'Aplikasi sudah menggunakan versi terbaru untuk kanal ini.';
                    setUpdateStatus(msg);
                    document.getElementById('about-update-details').innerText = msg;
                    installBtn.disabled = true;
                }
            } catch (error) {
                setUpdateStatus('Gagal memeriksa update: ' + (error.message || error), true);
            } finally {
                if (btn) { btn.disabled = false; btn.innerText = '🔎 Periksa Update'; }
            }
        }

        function formatBytes(bytes) {
            if (!Number.isFinite(bytes) || bytes < 0) return '—';
            if (bytes < 1024) return bytes + ' B';
            const units = ['KB', 'MB', 'GB', 'TB'];
            let value = bytes / 1024, unit = 0;
            while (value >= 1024 && unit < units.length - 1) { value /= 1024; unit++; }
            return value.toFixed(1) + ' ' + units[unit];
        }

        function formatEta(seconds) {
            if (!Number.isFinite(seconds) || seconds < 0) return 'menghitung…';
            const s = Math.ceil(seconds);
            if (s < 60) return s + ' dtk';
            return Math.floor(s / 60) + ' m ' + (s % 60) + ' dtk';
        }

        async function refreshUpdateProgress() {
            try {
                if (!window.pywebview?.api?.get_update_progress) return;
                const p = await window.pywebview.api.get_update_progress();
                const panel = document.getElementById('update-progress-panel');
                panel.classList.remove('hidden');
                const percent = Number(p.percent) || 0;
                document.getElementById('update-progress-label').innerText = p.status || 'Mengunduh update…';
                document.getElementById('update-progress-percent').innerText = p.total > 0 ? Math.floor(percent) + '%' : formatBytes(p.downloaded || 0);
                document.getElementById('update-progress-bar').style.width = Math.min(100, Math.max(0, percent)) + '%';
                const totalText = p.total > 0 ? formatBytes(p.downloaded || 0) + ' / ' + formatBytes(p.total) : formatBytes(p.downloaded || 0) + ' diunduh';
                const speedText = formatBytes(p.speed_bps || 0) + '/dtk';
                const etaText = p.total > 0 && p.eta_seconds != null ? formatEta(Number(p.eta_seconds)) : '—';
                document.getElementById('update-progress-details').innerText = totalText + ' · ' + speedText + ' · Sisa ' + etaText;
            } catch (_) {}
        }

        async function installAvailableUpdate() {
            if (!availableUpdate || !window.pywebview || !window.pywebview.api || updateInstallInProgress) return;
            updateInstallInProgress = true;
            const btn = document.getElementById('btn-install-update');
            btn.disabled = true;
            btn.innerText = 'Mengunduh…';
            setUpdateStatus('Mengunduh update dan menyiapkan restart…');
            document.getElementById('update-progress-panel').classList.remove('hidden');
            await refreshUpdateProgress();
            const progressTimer = setInterval(refreshUpdateProgress, 500);
            try {
                const result = await window.pywebview.api.install_update(availableUpdate.tag_name, document.getElementById('setting-update-channel').value);
                clearInterval(progressTimer);
                await refreshUpdateProgress();
                if (!result || !result.success) throw new Error((result && result.error) || 'Pemasangan update gagal.');
                document.getElementById('update-progress-bar').style.width = '100%';
                document.getElementById('update-progress-percent').innerText = '100%';
                setUpdateStatus('Update terpasang. Aplikasi akan dimulai ulang…');
            } catch (error) {
                clearInterval(progressTimer);
                setUpdateStatus('Gagal memasang update: ' + (error.message || error), true);
                updateInstallInProgress = false;
                btn.disabled = false;
                btn.innerText = '⬇ Unduh & Pasang';
            }
        }

        function openExternalUrl(url) {
            if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.open_url === 'function') {
                window.pywebview.api.open_url(url);
            } else {
                window.open(url, '_blank');
            }
        }

        function savePopupPreferences() {
            localStorage.setItem('suppress_tower_popup', String(document.getElementById('suppress-tower-popup').checked));
            localStorage.setItem('suppress_internet_popup', String(document.getElementById('suppress-internet-popup').checked));
        }

        function resetPopupPreferences() {
            localStorage.removeItem('suppress_tower_popup');
            localStorage.removeItem('suppress_internet_popup');
            document.getElementById('suppress-tower-popup').checked = false;
            document.getElementById('suppress-internet-popup').checked = false;
        }

        function shouldShowIssuePopup(kind) {
            const key = kind === 'tower' ? 'suppress_tower_popup' : 'suppress_internet_popup';
            return localStorage.getItem(key) !== 'true';
        }

        function openModal(modalId, boxId) {
            let modal = document.getElementById(modalId);
            let box = document.getElementById(boxId);
            modal.classList.remove('opacity-0', 'pointer-events-none');
            box.classList.remove('scale-95');
            box.classList.add('scale-100');
        }

        function closeModal(modalId, boxId) {
            let modal = document.getElementById(modalId);
            let box = document.getElementById(boxId);
            modal.classList.add('opacity-0', 'pointer-events-none');
            box.classList.remove('scale-100');
            box.classList.add('scale-95');
        }

        function clearPingToolHistory() {
            const output = document.getElementById('ping-output');
            if (output) {
                output.innerText = 'Riwayat ping dibersihkan.';
                output.scrollTop = 0;
                output.classList.remove('animate-pulse');
            }
        }

        function toggleSettingsModal() {
            let modal = document.getElementById('settingsModal');
            if (modal.classList.contains('pointer-events-none')) {
                resizeSettingsContent(activeSettingsTab, false);
                openModal('settingsModal', 'settingsBox');
            } else {
                clearPingToolHistory();
                closeModal('settingsModal', 'settingsBox');
            }
        }

        function toggleHistoryModal() {
            let modal = document.getElementById('historyModal');
            if (modal.classList.contains('pointer-events-none')) {
                openModal('historyModal', 'historyBox');
                unreadCount = 0;
                let badge = document.getElementById('bell-badge');
                badge.innerText = '0';
                badge.classList.add('hidden');
            } else {
                closeModal('historyModal', 'historyBox');
            }
        }

        function closeDisconnectModal() {
            closeModal('disconnectModal', 'disconnectBox');
        }

        function closeReconnectModal() {
            closeModal('reconnectModal', 'reconnectBox');
        }

        function changeTheme(theme, save = true) {
            let body = document.getElementById('app-body');
            if (theme === 'light') {
                body.className = body.className.replace('bg-slate-950 text-slate-100', 'bg-slate-100 text-slate-900');
            } else {
                body.className = body.className.replace('bg-slate-100 text-slate-900', 'bg-slate-950 text-slate-100');
            }
            if (save) {
                localStorage.setItem('router_theme', theme);
            }
        }

        function changeFrequency(val) {
            currentIntervalTime = parseInt(val, 10) || 1000;
            localStorage.setItem('router_freq', String(currentIntervalTime));
            if (window.pywebview && window.pywebview.api) startPolling();
            updatePingMonitorFrequency();
        }

        function addHistoryLog(status, timeStr) {
            const isConn = status.includes('Tersambung') || status.includes('Normal');
            const logItem = { status: status, time: timeStr, type: isConn ? 'connect' : 'disconnect' };
            connectionHistory.unshift(logItem);
            
            let modal = document.getElementById('historyModal');
            if (modal.classList.contains('pointer-events-none')) {
                unreadCount++;
                let badge = document.getElementById('bell-badge');
                badge.innerText = unreadCount;
                badge.classList.remove('hidden');
            }
            renderHistoryList();
        }

        function renderHistoryList() {
            let container = document.getElementById('history-list');
            if (connectionHistory.length === 0) {
                container.innerHTML = '<div class="text-center text-slate-500 py-6">Belum ada riwayat tercatat dalam sesi ini.</div>';
                return;
            }
            let html = '';
            connectionHistory.forEach(item => {
                let badgeColor = item.type === 'connect' ? 'bg-emerald-950/50 text-emerald-400 border-emerald-500/30' : 'bg-orange-950/50 text-orange-400 border-orange-500/30';
                let icon = item.type === 'connect' ? '🟢' : '🟠';
                html += `
                    <div class="bg-slate-950/60 border border-slate-800/80 p-2.5 rounded-xl flex items-center justify-between">
                        <div class="flex items-center gap-2">
                            <span>${icon}</span>
                            <div>
                                <div class="font-semibold text-slate-200">${item.status}</div>
                                <div class="text-[10px] text-slate-400">Pukul ${item.time}</div>
                            </div>
                        </div>
                        <span class="text-[10px] px-2 py-0.5 rounded-full border ${badgeColor}">${item.type === 'connect' ? 'Normal' : 'Gangguan'}</span>
                    </div>
                `;
            });
            container.innerHTML = html;
        }

        function clearHistory() {
            connectionHistory = [];
            unreadCount = 0;
            document.getElementById('bell-badge').classList.add('hidden');
            renderHistoryList();
        }

        // Animated Smooth Line Charts with Chart.js
        function createChart(ctx, color) {
            return new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        data: [],
                        borderColor: color,
                        backgroundColor: color + '15',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.35,
                        pointRadius: 2,
                        pointBackgroundColor: '#ffffff',
                        pointBorderColor: color,
                        pointBorderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { duration: 260, easing: 'easeOutQuart' },
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { display: false },
                        y: { 
                            grid: { color: 'rgba(51, 65, 85, 0.15)' },
                            ticks: { font: { size: 9 }, color: '#94a3b8', maxTicksLimit: 3 }
                        }
                    }
                }
            });
        }

        const chartRsrp = createChart(document.getElementById('chartRsrp').getContext('2d'), '#06b6d4');
        const chartRssi = createChart(document.getElementById('chartRssi').getContext('2d'), '#3b82f6');
        const chartRsrq = createChart(document.getElementById('chartRsrq').getContext('2d'), '#f97316');
        const chartSinr = createChart(document.getElementById('chartSinr').getContext('2d'), '#10b981');
        const chartPing = createChart(document.getElementById('chartPing').getContext('2d'), '#e879f9');
        let pingMonitorTimer = null;
        let pingMonitorBusy = false;
        let pingMonitorInterval = Number.parseInt(localStorage.getItem('router_ping_freq') || '2000', 10);
        if (!Number.isFinite(pingMonitorInterval) || pingMonitorInterval < 1000 || pingMonitorInterval > 3600000) pingMonitorInterval = 2000;

        function getStatusInfo(type, val, isConnected) {
            if (!isConnected) {
                return { text: 'Koneksi Terputus', color: 'bg-orange-600', textCol: 'text-orange-400' };
            }
            if (val === null || val === undefined || isNaN(val)) return { text: 'N/A', color: 'bg-slate-500', textCol: 'text-slate-400' };
            
            if (type === 'rsrp') {
                if (val >= -80) return { text: 'Mantap', color: 'bg-purple-700', textCol: 'text-purple-400' };
                if (val >= -95) return { text: 'Bagus', color: 'bg-emerald-500', textCol: 'text-emerald-400' };
                if (val >= -110) return { text: 'Cukup', color: 'bg-amber-500', textCol: 'text-amber-400' };
                return { text: 'Buruk', color: 'bg-red-500', textCol: 'text-red-400' };
            } else if (type === 'rssi') {
                if (val >= -70) return { text: 'Mantap', color: 'bg-purple-700', textCol: 'text-purple-400' };
                if (val >= -85) return { text: 'Bagus', color: 'bg-emerald-500', textCol: 'text-emerald-400' };
                if (val >= -100) return { text: 'Cukup', color: 'bg-amber-500', textCol: 'text-amber-400' };
                return { text: 'Buruk', color: 'bg-red-500', textCol: 'text-red-400' };
            } else if (type === 'rsrq') {
                if (val >= -10) return { text: 'Mantap', color: 'bg-purple-700', textCol: 'text-purple-400' };
                if (val >= -15) return { text: 'Bagus', color: 'bg-emerald-500', textCol: 'text-emerald-400' };
                if (val >= -20) return { text: 'Cukup', color: 'bg-amber-500', textCol: 'text-amber-400' };
                return { text: 'Buruk', color: 'bg-red-500', textCol: 'text-red-400' };
            } else if (type === 'sinr') {
                if (val >= 20) return { text: 'Mantap', color: 'bg-purple-700', textCol: 'text-purple-400' };
                if (val >= 10) return { text: 'Bagus', color: 'bg-emerald-500', textCol: 'text-emerald-400' };
                if (val >= 0) return { text: 'Cukup', color: 'bg-amber-500', textCol: 'text-amber-400' };
                return { text: 'Buruk', color: 'bg-red-500', textCol: 'text-red-400' };
            }
            return { text: '-', color: 'bg-slate-500', textCol: 'text-slate-400' };
        }

        function startPingMonitor() {
            if (pingMonitorTimer) clearInterval(pingMonitorTimer);
            const samplePing = async () => {
                if (pingMonitorBusy || !window.pywebview || !window.pywebview.api || !window.pywebview.api.get_ping_latency) return;
                pingMonitorBusy = true;
                try {
                    const result = await window.pywebview.api.get_ping_latency();
                    const valueEl = document.getElementById('val-ping');
                    const textEl = document.getElementById('text-ping');
                    const dotEl = document.getElementById('dot-ping');
                    if (result && result.success && Number.isFinite(Number(result.value))) {
                        const value = Number(result.value);
                        valueEl.innerText = value.toFixed(1) + ' ms';
                        textEl.innerText = value < 80 ? 'Bagus' : value < 150 ? 'Sedang' : 'Tinggi';
                        textEl.className = 'font-semibold ' + (value < 80 ? 'text-emerald-400' : value < 150 ? 'text-amber-400' : 'text-orange-400');
                        dotEl.className = 'h-1.5 w-1.5 rounded-full ' + (value < 80 ? 'bg-emerald-400' : value < 150 ? 'bg-amber-400' : 'bg-orange-400');
                        if (chartPing.data.labels.length >= maxDataPoints) {
                            chartPing.data.labels.shift();
                            chartPing.data.datasets[0].data.shift();
                        }
                        chartPing.data.labels.push(new Date().toLocaleTimeString('id-ID'));
                        chartPing.data.datasets[0].data.push(value);
                        chartPing.update();
                    } else {
                        valueEl.innerText = '— ms';
                        textEl.innerText = 'Tidak tersedia';
                        textEl.className = 'font-semibold text-orange-400';
                        dotEl.className = 'h-1.5 w-1.5 rounded-full bg-orange-400';
                    }
                } catch (error) {
                    document.getElementById('val-ping').innerText = '— ms';
                    document.getElementById('text-ping').innerText = 'Tidak tersedia';
                } finally {
                    pingMonitorBusy = false;
                }
            };
            samplePing();
            pingMonitorTimer = setInterval(samplePing, pingMonitorInterval);
        }

        function updatePingMonitorFrequency(restart = true) {
            const select = document.getElementById('setting-ping-freq');
            if (select && select.value === 'auto') {
                pingMonitorInterval = Math.min(3600000, Math.max(1000, currentIntervalTime * 2));
                const title = document.getElementById('ping-chart-title');
                if (title) title.textContent = '📈 Ping Latency — setiap ' + (pingMonitorInterval / 1000) + ' detik (update ×2)';
                if (restart && window.pywebview && window.pywebview.api) startPingMonitor();
            }
        }

        function changePingFrequency(val) {
            const select = document.getElementById('setting-ping-freq');
            const customInput = document.getElementById('setting-ping-freq-custom');
            let interval;
            if (val === 'custom') {
                customInput.classList.remove('hidden');
                interval = Math.round(Number(customInput.value) * 1000);
                if (!Number.isFinite(interval) || interval < 1000 || interval > 3600000) return;
                pingMonitorInterval = interval;
                localStorage.setItem('router_ping_freq', String(interval));
                const title = document.getElementById('ping-chart-title');
                if (title) title.textContent = '📈 Ping Latency — setiap ' + (interval / 1000) + ' detik';
                if (window.pywebview && window.pywebview.api) startPingMonitor();
                return;
            }
            customInput.classList.add('hidden');
            if (val === 'auto') {
                localStorage.setItem('router_ping_freq', 'auto');
                updatePingMonitorFrequency();
            }
        }

        function showConnectionNotice(kind, message, autoHideMs = 0) {
            const banner = document.getElementById('floating-alert');
            const text = document.getElementById('floating-alert-text');
            if (!banner || !text) return;

            if (noticeTimer) {
                clearTimeout(noticeTimer);
                noticeTimer = null;
            }
            banner.classList.remove(
                'bg-orange-600/90', 'border-orange-400',
                'bg-emerald-600/90', 'border-emerald-400',
                'bg-cyan-600/90', 'border-cyan-400',
                'hidden', 'animate-bounce'
            );
            if (kind === 'recovered') {
                banner.classList.add('bg-emerald-600/90', 'border-emerald-400');
            } else if (kind === 'info') {
                banner.classList.add('bg-cyan-600/90', 'border-cyan-400');
            } else {
                banner.classList.add('bg-orange-600/90', 'border-orange-400');
            }
            banner.classList.add('flex');
            text.innerText = message;
            if (autoHideMs > 0) {
                noticeTimer = setTimeout(() => {
                    banner.classList.add('hidden');
                    noticeTimer = null;
                }, autoHideMs);
            }
        }

        function updateUI(data) {
            const now = new Date();
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            const nowTime = `${hours}:${minutes}:${seconds}`;

            const parsedSignalBar = Number.parseInt(data.signalbar, 10);
            const rawTowerConnected = Number.isFinite(parsedSignalBar) && parsedSignalBar > 0;
            const rawInternetOk = data.internet_ok === true;

            const towerStatusEl = document.getElementById('tower-status-val');
            const internetStatusEl = document.getElementById('internet-status-val');
            const floatingAlert = document.getElementById('floating-alert');

            // First sample establishes baseline without a false "recovered" alert.
            if (wasConnected === null) {
                wasConnected = rawTowerConnected;
                wasInternetOk = rawTowerConnected && rawInternetOk;
                towerSuccessCount = rawTowerConnected ? 1 : 0;
                towerFailCount = rawTowerConnected ? 0 : 1;
                internetSuccessCount = wasInternetOk ? 1 : 0;
                internetFailCount = wasInternetOk ? 0 : 1;
                if (!wasConnected) {
                    towerIssueNotified = true;
                    if (shouldShowIssuePopup('tower')) {
                        showConnectionNotice('issue', '⚠️ GANGGUAN TOWER: sinyal tower tidak terdeteksi.');
                    }
                } else if (!wasInternetOk) {
                    internetIssueNotified = true;
                    if (shouldShowIssuePopup('internet')) {
                        showConnectionNotice('issue', '🌐 GANGGUAN INTERNET: tower tersambung, akses internet gagal.');
                    }
                }
            } else {
                // Require repeated readings before changing state; this prevents transient request
                // failures from alternating between "gangguan" and "kembali normal".
                if (rawTowerConnected) {
                    towerSuccessCount++;
                    towerFailCount = 0;
                    if (!wasConnected && towerSuccessCount >= 3) {
                        wasConnected = true;
                        addHistoryLog('Tower Kembali Normal', nowTime);
                        playAlertSound();
                        if (towerIssueNotified) {
                            showConnectionNotice('recovered', '✅ TOWER KEMBALI NORMAL.', 9000);
                        }
                        towerIssueNotified = false;
                    }
                } else {
                    towerFailCount++;
                    towerSuccessCount = 0;
                    if (wasConnected && towerFailCount >= 3) {
                        wasConnected = false;
                        wasInternetOk = false;
                        addHistoryLog('Tower Terputus', nowTime);
                        playAlertSound();
                        towerIssueNotified = true;
                        if (shouldShowIssuePopup('tower')) {
                            showConnectionNotice('issue', '⚠️ GANGGUAN TOWER: koneksi tower terputus.');
                        }
                    }
                }

                if (!wasConnected) {
                    wasInternetOk = false;
                    // Start a fresh internet-failure debounce after the tower is back.
                    internetFailCount = 0;
                    internetSuccessCount = 0;
                } else if (rawInternetOk) {
                    internetSuccessCount++;
                    internetFailCount = 0;
                    if (!wasInternetOk && internetSuccessCount >= 3) {
                        wasInternetOk = true;
                        if (internetIssueNotified) {
                            addHistoryLog('Internet Kembali Normal', nowTime);
                            playAlertSound();
                            showConnectionNotice('recovered', '✅ INTERNET KEMBALI NORMAL.', 9000);
                        }
                        internetIssueNotified = false;
                    }
                } else {
                    internetFailCount++;
                    internetSuccessCount = 0;
                    if (internetFailCount >= 3 && !internetIssueNotified) {
                        wasInternetOk = false;
                        internetIssueNotified = true;
                        addHistoryLog('Internet Bermasalah', nowTime);
                        playAlertSound();
                        if (shouldShowIssuePopup('internet')) {
                            showConnectionNotice('issue', '🌐 GANGGUAN INTERNET: tower aktif, tetapi akses internet gagal.');
                        }
                    }
                }
            }

            // Keep the visible state tied to the debounced state, not one transient request.
            const isConnected = wasConnected === true;
            const internetOk = isConnected && wasInternetOk === true;

            if (!isConnected) {
                towerStatusEl.innerText = 'Terputus';
                towerStatusEl.className = 'text-[11px] font-bold text-orange-500 mt-0.5 truncate';
                internetStatusEl.innerText = 'Tidak tersedia';
                internetStatusEl.className = 'text-[11px] font-bold text-orange-500 mt-0.5 truncate';
            } else {
                towerStatusEl.innerText = 'Tersambung';
                towerStatusEl.className = 'text-[11px] font-bold text-emerald-400 mt-0.5 truncate';
                if (internetOk) {
                    internetStatusEl.innerText = 'Normal';
                    internetStatusEl.className = 'text-[11px] font-bold text-emerald-400 mt-0.5 truncate';
                } else {
                    internetStatusEl.innerText = 'Bermasalah';
                    internetStatusEl.className = 'text-[11px] font-bold text-orange-500 mt-0.5 truncate';
                }
            }

            let rsrp, rssi, rsrq, sinr;
            if (!isConnected) {
                rsrp = -120;
                rssi = -120;
                rsrq = -120;
                sinr = 0;
            } else {
                rsrp = parseFloat(data.nr5g_rsrp) || 0;
                rssi = parseFloat(data.nr5g_rssi) || 0;
                rsrq = parseFloat(data.nr5g_rsrq) || 0;
                sinr = parseFloat(data.nr5g_snr) || 0;
            }

            document.getElementById('val-rsrp').innerText = rsrp + ' dBm';
            document.getElementById('val-rssi').innerText = rssi + ' dBm';
            document.getElementById('val-rsrq').innerText = rsrq + ' dB';
            document.getElementById('val-sinr').innerText = sinr + ' dB';

            function applyStatus(prefix, type, val) {
                let status = getStatusInfo(type, val, isConnected);
                document.getElementById(`text-${prefix}`).innerText = status.text;
                document.getElementById(`text-${prefix}`).className = `font-semibold ${status.textCol}`;
                document.getElementById(`dot-${prefix}`).className = `h-1.5 w-1.5 rounded-full ${status.color}`;
            }

            applyStatus('rsrp', 'rsrp', rsrp);
            applyStatus('rssi', 'rssi', rssi);
            applyStatus('rsrq', 'rsrq', rsrq);
            applyStatus('sinr', 'sinr', sinr);

            // Smooth chart animation update
            function updateChartData(chart, val) {
                if (chart.data.labels.length >= maxDataPoints) {
                    chart.data.labels.shift();
                    chart.data.datasets[0].data.shift();
                }
                chart.data.labels.push(nowTime);
                chart.data.datasets[0].data.push(val);
                // Keep a short smooth transition; the fixed-size history prevents runaway points.
                chart.update();
            }

            updateChartData(chartRsrp, rsrp);
            updateChartData(chartRssi, rssi);
            updateChartData(chartRsrq, rsrq);
            updateChartData(chartSinr, sinr);

            // Static info without animations
            document.getElementById('info-pci').innerText = data.nr5g_pci || '-';
            document.getElementById('info-cellid').innerText = data.nr5g_cell_id || '-';
            document.getElementById('info-nettype').innerText = data.network_type || '-';
            document.getElementById('info-signalbar').innerText = (data.signalbar || '0') + ' / 3';
            document.getElementById('info-band').innerText = data.wan_active_band || '-';

            let connEl = document.getElementById('status-conn');
            connEl.innerText = `Terakhir: ${nowTime}`;
            connEl.className = "text-[11px] font-medium bg-emerald-950/40 border border-emerald-500/30 text-emerald-400 px-3 py-1 rounded-xl shadow-inner";
        }

        async function fetchTelemetry() {
            try {
                let res = await window.pywebview.api.get_router_data();
                if (res && Object.keys(res).length > 0) {
                    updateUI(res);
                } else {
                    updateUI({ signalbar: "0", internet_ok: false });
                    const connEl = document.getElementById('status-conn');
                    connEl.innerText = 'Router tidak merespons';
                    connEl.className = "text-[11px] font-medium bg-red-950/40 border border-red-500/30 text-red-400 px-3 py-1 rounded-xl shadow-inner";
                }
            } catch (err) {
                console.error("Gagal ambil data:", err);
                updateUI({ signalbar: "0", internet_ok: false });
                const connEl = document.getElementById('status-conn');
                connEl.innerText = "Terputus...";
                connEl.className = "text-[11px] font-medium bg-red-950/40 border border-red-500/30 text-red-400 px-3 py-1 rounded-xl shadow-inner";
            }
        }
    </script>
</body>
</html>
"""
HTML_CONTENT = HTML_CONTENT.replace("__APP_VERSION__", APP_VERSION)

class Api:
    def __init__(self):
        self._update_progress = {
            "active": False, "percent": 0, "downloaded": 0, "total": 0,
            "speed_bps": 0, "eta_seconds": None, "status": "Siap", "error": None,
        }
        self._update_progress_lock = threading.Lock()

    def get_update_progress(self):
        with self._update_progress_lock:
            return dict(self._update_progress)

    def _set_update_progress(self, **values):
        with self._update_progress_lock:
            self._update_progress.update(values)

    def get_router_data(self):
        data = {}
        internet_ok = False
        try:
            url = f"http://192.168.0.1/ubus/?t={int(time.time() * 1000)}"
            headers = {
                "Content-Type": "application/json",
                "Referer": "http://192.168.0.1/index.html",
                "Origin": "http://192.168.0.1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36",
                "z-mode": "0",
                "z-tag": "nwinfo_get_netinfo",
                "X-Requested-With": "XMLHttpRequest"
            }
            payload = [
                {
                    "jsonrpc": "2.0",
                    "method": "call",
                    "params": [
                        "00000000000000000000000000000000",
                        "zte_nwinfo_api",
                        "nwinfo_get_netinfo",
                        {}
                    ],
                    "id": 1
                }
            ]
            resp = requests.post(url, json=payload, headers=headers, timeout=3, verify=False)
            
            if resp.text.strip().startswith("[") or resp.text.strip().startswith("{"):
                json_array = resp.json()
                if isinstance(json_array, list) and len(json_array) > 0:
                    res = json_array[0].get("result")
                    if isinstance(res, list) and len(res) > 1 and isinstance(res[1], dict):
                        data = res[1]
        except Exception as e:
            print(f"[ERROR TOWER] {e}")

        # Do not report internet as normal if router telemetry/tower signal is unavailable.
        try:
            signal_bar = int(str(data.get("signalbar", "0")).strip())
        except (TypeError, ValueError):
            signal_bar = 0

        if signal_bar > 0:
            # Check two independent HTTPS endpoints. A temporary failure or block on one
            # provider should not falsely mark the whole internet connection as down.
            internet_ok = False
            probes = (
                "https://www.cloudflare.com/cdn-cgi/trace",
                "https://www.google.com/generate_204",
            )
            for probe_url in probes:
                try:
                    response = requests.get(
                        probe_url,
                        headers={"Cache-Control": "no-cache"},
                        timeout=(1.5, 2.0),
                    )
                    response.raise_for_status()
                    internet_ok = True
                    break
                except requests.exceptions.RequestException:
                    continue
        else:
            internet_ok = False

        data["internet_ok"] = internet_ok
        return data

    @staticmethod
    def _valid_ping_host(host):
        """Accept only IP addresses or conventional DNS hostnames."""
        import ipaddress
        import re

        if not isinstance(host, str):
            return False
        host = host.strip()
        if not host or len(host) > 253 or host.startswith('-'):
            return False
        try:
            ipaddress.ip_address(host)
            return True
        except ValueError:
            if re.fullmatch(r"[0-9.]+", host):
                return False

        # DNS labels: 1-63 chars, alphanumeric ends, hyphens only internally.
        hostname_pattern = re.compile(
            r"(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)"
            r"(?:\.(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?))*\.?$"
        )
        return bool(hostname_pattern.fullmatch(host))

    def run_ping(self, host="1.1.1.1"):
        if not self._valid_ping_host(host):
            return {"success": False, "output": "Host/IP tidak valid. Gunakan alamat IP atau nama host DNS yang valid (maksimal 253 karakter)."}
        host = host.strip()
        try:
            param = "-n" if platform.system().lower() == "windows" else "-c"
            command = ["ping", param, "4", host]
            # Prevent a console window flashing when ping is triggered from the
            # GUI in both frozen EXE and regular Python launches on Windows.
            run_options = {
                "stdout": subprocess.PIPE,
                "stderr": subprocess.STDOUT,
                "text": True,
                "timeout": 20,
                "check": False,
                "shell": False,
            }
            if platform.system().lower() == "windows":
                run_options["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
                run_options["startupinfo"] = startupinfo
            completed = subprocess.run(command, **run_options)
            output = completed.stdout or ""
            if completed.returncode == 0:
                return {"success": True, "output": output}
            return {"success": False, "output": output or f"Ping keluar dengan kode {completed.returncode}."}
        except subprocess.TimeoutExpired as e:
            partial = e.stdout or ""
            if isinstance(partial, bytes):
                partial = partial.decode(errors="replace")
            return {"success": False, "output": f"Ping timeout.\n{partial}"}
        except Exception as e:
            return {"success": False, "output": str(e)}

    def get_ping_latency(self):
        """Measure HTTPS round-trip latency to Cloudflare (not ICMP ping)."""
        try:
            started = time.perf_counter()
            response = requests.get(
                f"https://www.cloudflare.com/cdn-cgi/trace?_={time.time_ns()}",
                timeout=(1.5, 2.0)
            )
            response.raise_for_status()
            return {"success": True, "value": round((time.perf_counter() - started) * 1000, 1)}
        except Exception as e:
            return {"success": False, "error": f"{type(e).__name__}: {e}"}

    @staticmethod
    def _release_version_key(tag):
        import re
        numbers = re.findall(r"\d+", str(tag or ""))
        return tuple(int(n) for n in numbers) if numbers else (0,)

    def _get_release(self, channel):
        channel = "beta" if channel == "beta" else "stable"
        response = requests.get(
            GITHUB_RELEASES_API,
            headers={"Accept": "application/vnd.github+json", "User-Agent": "IRA-ZTE-Live-Signal-Charts"},
            timeout=(3, 8),
        )
        response.raise_for_status()
        releases = response.json()
        if not isinstance(releases, list):
            raise RuntimeError("Respons GitHub Releases tidak valid.")
        candidates = [
            release for release in releases
            if isinstance(release, dict) and not release.get("draft", False)
            and (bool(release.get("prerelease")) if channel == "beta" else not bool(release.get("prerelease")))
        ]
        if not candidates:
            return None
        # GitHub returns releases newest-first; sort defensively by published date.
        candidates.sort(key=lambda r: str(r.get("published_at") or r.get("created_at") or ""), reverse=True)
        return candidates[0]

    @staticmethod
    def _running_app_kind():
        """Return the release asset type for this installed desktop app."""
        return "exe" if getattr(sys, "frozen", False) else "python"

    @staticmethod
    def _release_asset_for_kind(assets, kind):
        """Select only the exact asset type supported by the current app."""
        if not isinstance(assets, list):
            return None

        def name_of(asset):
            return str(asset.get("name") or "").strip()

        if kind == "exe":
            # The EXE workflow publishes versioned names such as
            # IRA_ZTE_Live_Signal_Charts-1.2.3.exe.
            matches = [
                asset for asset in assets
                if isinstance(asset, dict)
                and name_of(asset).lower().endswith(".exe")
                and "ira_zte_live_signal_charts" in name_of(asset).lower()
            ]
        elif kind == "python":
            allowed = {
                "router_app.py",
                "ira_zte_speed_test_stable.py",
                "ira-zte-live-signal-charts.py",
                "app.py",
            }
            matches = [
                asset for asset in assets
                if isinstance(asset, dict) and name_of(asset).lower() in allowed
            ]
        elif kind == "apk":
            matches = [
                asset for asset in assets
                if isinstance(asset, dict)
                and name_of(asset).lower().endswith(".apk")
                and "ira_zte_live_signal_charts" in name_of(asset).lower()
            ]
        else:
            return None

        return matches[0] if matches else None

    def check_for_updates(self, channel="stable"):
        try:
            release = self._get_release(channel)
            if release is None:
                kind = "beta/pre-release" if channel == "beta" else "stable"
                return {"update_available": False, "message": f"Belum ada release {kind} yang dipublikasikan di GitHub."}
            tag = str(release.get("tag_name") or "").strip()
            if not tag:
                return {"update_available": False, "error": "Release ditemukan tetapi tidak memiliki tag versi."}

            app_kind = self._running_app_kind()
            asset = self._release_asset_for_kind(release.get("assets") or [], app_kind)
            current_key = self._release_version_key(APP_VERSION)
            remote_key = self._release_version_key(tag)
            is_newer = remote_key > current_key or (remote_key == current_key and tag.lower() != APP_VERSION.lower())
            can_install = bool(is_newer and asset and asset.get("browser_download_url"))
            kind_label = {"exe": "EXE", "python": "Python", "apk": "APK"}[app_kind]
            return {
                "update_available": can_install,
                "current_version": APP_VERSION,
                "tag_name": tag,
                "name": release.get("name") or tag,
                "body": release.get("body") or "",
                "published_at": release.get("published_at"),
                "html_url": release.get("html_url"),
                "channel": "beta" if release.get("prerelease") else "stable",
                "app_kind": app_kind,
                "asset_name": asset.get("name") if asset else None,
                "asset_url": asset.get("browser_download_url") if asset else None,
                "message": (
                    f"Update tersedia ({kind_label})." if can_install else
                    f"Release terbaru tidak memiliki aset {kind_label} yang cocok; aset jenis lain tidak akan diunduh."
                    if is_newer and not asset else
                    "Aplikasi sudah menggunakan versi terbaru untuk kanal ini."
                ),
            }
        except requests.exceptions.RequestException as e:
            return {"update_available": False, "error": f"Tidak dapat menghubungi GitHub: {type(e).__name__}: {e}"}
        except Exception as e:
            return {"update_available": False, "error": f"Gagal memeriksa release: {type(e).__name__}: {e}"}

    def install_update(self, tag_name, channel="stable"):
        """Install only the release asset matching the current desktop app type."""
        try:
            release = self._get_release(channel)
            if not release or str(release.get("tag_name")) != str(tag_name):
                return {"success": False, "error": "Release berubah sejak pemeriksaan. Periksa update kembali."}

            app_kind = self._running_app_kind()
            asset = self._release_asset_for_kind(release.get("assets") or [], app_kind)
            if not asset or not asset.get("browser_download_url"):
                kind_label = "EXE" if app_kind == "exe" else "Python"
                return {"success": False, "error": f"Release ini tidak memiliki aset {kind_label} yang cocok; aplikasi tidak diubah."}

            self._set_update_progress(active=True, percent=0, downloaded=0, total=0,
                                      speed_bps=0, eta_seconds=None, status="Menghubungkan ke server…", error=None)
            started_at = time.monotonic()
            downloaded = 0
            chunks = []
            try:
                with requests.get(
                    asset["browser_download_url"],
                    headers={"User-Agent": "IRA-ZTE-Live-Signal-Charts"},
                    timeout=(5, 60), stream=True,
                ) as response:
                    response.raise_for_status()
                    total = int(response.headers.get("Content-Length") or 0)
                    self._set_update_progress(total=total, status="Mengunduh update…")
                    for chunk in response.iter_content(chunk_size=128 * 1024):
                        if not chunk:
                            continue
                        chunks.append(chunk)
                        downloaded += len(chunk)
                        elapsed = max(time.monotonic() - started_at, 0.001)
                        speed = downloaded / elapsed
                        eta = max((total - downloaded) / speed, 0) if total > 0 and speed > 0 else None
                        percent = min(downloaded * 100 / total, 100) if total > 0 else 0
                        self._set_update_progress(
                            downloaded=downloaded, total=total, speed_bps=round(speed),
                            eta_seconds=round(eta) if eta is not None else None,
                            percent=round(percent, 1), status="Mengunduh update…",
                        )
                payload = b"".join(chunks)
                self._set_update_progress(active=False, percent=100, downloaded=downloaded,
                                          total=total, status="Unduhan selesai, memvalidasi file…")
            except Exception:
                self._set_update_progress(active=False, status="Unduhan gagal.")
                raise

            if app_kind == "python":
                if len(payload) < 1000 or b"class Api" not in payload or b"HTML_CONTENT" not in payload:
                    return {"success": False, "error": "File release tidak tampak seperti source Python aplikasi yang valid; file tidak diganti."}
                import re
                current_script = Path(__file__).resolve()
                decoded_source = payload.decode("utf-8-sig")
                decoded_source, replacements = re.subn(
                    r'^APP_VERSION\s*=\s*["\'][^"\']*["\']',
                    f'APP_VERSION = "{tag_name}"',
                    decoded_source, count=1, flags=re.MULTILINE,
                )
                decoded_source, js_replacements = re.subn(
                    r"""^\s*const APP_VERSION_JS = ['"][^'"]*['"];""",
                    f"        const APP_VERSION_JS = '{tag_name}';",
                    decoded_source, count=1, flags=re.MULTILINE,
                )
                if replacements != 1 or js_replacements != 1:
                    return {"success": False, "error": "Source release tidak memiliki penanda versi yang didukung; file tidak diganti."}
                compile(decoded_source, str(current_script), "exec")
                temp_path = current_script.with_suffix(current_script.suffix + ".update")
                temp_path.write_text(decoded_source, encoding="utf-8")
                os.replace(temp_path, current_script)
                threading.Timer(1.2, self._restart_after_update, args=(str(current_script),)).start()
                return {"success": True, "version": tag_name, "message": "Update Python terpasang; aplikasi akan dimulai ulang."}

            # Windows cannot overwrite a running executable. Download and validate the
            # matching EXE first, then use a short-lived batch file to replace it after exit.
            if len(payload) < 100_000 or not payload.startswith(b"MZ"):
                return {"success": False, "error": "File release bukan executable Windows yang valid; file tidak diganti."}
            current_exe = Path(sys.executable).resolve()
            if not getattr(sys, "frozen", False):
                return {"success": False, "error": "Updater EXE hanya dapat dijalankan dari aplikasi EXE."}
            temp_exe = current_exe.with_name(current_exe.stem + ".update.exe")
            temp_exe.write_bytes(payload)
            import subprocess
            import tempfile
            batch_path = current_exe.with_name(current_exe.stem + "_update.bat")
            batch_path.write_text(
                "@echo off\\r\\n"
                "timeout /t 2 /nobreak >nul\\r\\n"
                f'move /y "{temp_exe}" "{current_exe}" >nul\\r\\n'
                f'if errorlevel 1 exit /b 1\\r\\n'
                f'start "" "{current_exe}"\\r\\n'
                f'del "%~f0"\\r\\n',
                encoding="utf-8",
            )
            subprocess.Popen(
                ["cmd.exe", "/c", str(batch_path)],
                cwd=str(current_exe.parent),
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                close_fds=True,
            )
            os._exit(0)
        except Exception as e:
            self._set_update_progress(active=False, status="Pembaruan gagal.", error=f"{type(e).__name__}: {e}")
            return {"success": False, "error": f"Pembaruan gagal: {type(e).__name__}: {e}"}

    @staticmethod
    def _restart_after_update(script_path):
        try:
            subprocess.Popen([sys.executable, script_path], cwd=str(Path(script_path).parent))
            os._exit(0)
        except Exception as e:
            print(f"[UPDATE RESTART ERROR] {e}")

    def open_url(self, url):
        from urllib.parse import urlparse
        import webbrowser
        parsed = urlparse(str(url))
        if parsed.scheme not in {"https"} or parsed.netloc not in {"github.com", "www.github.com"}:
            return {"success": False, "error": "URL eksternal tidak diizinkan."}
        webbrowser.open(url)
        return {"success": True}

    def run_speed_sample(self, mode):
        """Measure one bounded sample against Cloudflare's public speed-test endpoints."""
        endpoint = "https://speed.cloudflare.com"
        if mode not in {"download", "upload", "latency"}:
            return {"success": False, "error": "Mode speed test tidak valid."}

        try:
            cache_bust = time.time_ns()

            if mode == "latency":
                started = time.perf_counter()
                response = requests.get(
                    f"{endpoint}/__down?bytes=0&cacheBust={cache_bust}",
                    headers={"Cache-Control": "no-cache", "Pragma": "no-cache"},
                    timeout=(4, 5),
                )
                response.raise_for_status()
                value = (time.perf_counter() - started) * 1000
                return {"success": True, "value": round(value, 1), "unit": "ms"}

            if mode == "download":
                # Avoid a 100 MB request that can stall on slow or filtered connections.
                # Use a bounded 1.25-second measurement and retry a smaller payload if needed.
                last_error = None
                for byte_count in (25_000_000, 10_000_000):
                    started = time.perf_counter()
                    received = 0
                    try:
                        with requests.get(
                            f"{endpoint}/__down?bytes={byte_count}&cacheBust={cache_bust}",
                            headers={
                                "Cache-Control": "no-cache",
                                "Pragma": "no-cache",
                                "Accept-Encoding": "identity",
                                "User-Agent": "IRA-ZTE-Live-Signal-Charts/0.0.0-dev",
                            },
                            stream=True,
                            timeout=(3, 3),
                        ) as response:
                            response.raise_for_status()
                            for chunk in response.iter_content(chunk_size=64 * 1024):
                                if chunk:
                                    received += len(chunk)
                                elapsed_now = time.perf_counter() - started
                                if elapsed_now >= 1.25:
                                    break
                        elapsed = max(time.perf_counter() - started, 0.001)
                        if received > 0:
                            value = (received * 8 / elapsed) / 1_000_000
                            return {"success": True, "value": round(value, 2), "unit": "Mbps", "bytes_received": received}
                        last_error = "Server tidak mengirim data download."
                    except requests.exceptions.RequestException as e:
                        last_error = f"{type(e).__name__}: {e}"
                raise RuntimeError(f"Download gagal dari Cloudflare Speed Test: {last_error or 'tidak ada data yang diterima'}")

            # Measure upload throughput with a moderate payload; timeout prevents a stalled phase.
            payload = b"0" * 512_000
            started = time.perf_counter()
            response = requests.post(
                f"{endpoint}/__up?cacheBust={cache_bust}",
                data=payload,
                headers={
                    "Content-Type": "application/octet-stream",
                    "Cache-Control": "no-cache",
                },
                timeout=(4, 10),
            )
            response.raise_for_status()
            elapsed = max(time.perf_counter() - started, 0.001)
            value = (len(payload) * 8 / elapsed) / 1_000_000
            return {"success": True, "value": round(value, 2), "unit": "Mbps"}

        except requests.exceptions.Timeout:
            return {"success": False, "error": "Server speed test timeout (koneksi lambat atau endpoint diblokir)."}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Koneksi speed test gagal: {type(e).__name__}: {e}"}
        except Exception as e:
            return {"success": False, "error": f"{type(e).__name__}: {e}"}

if __name__ == '__main__':
    api = Api()
    window = webview.create_window(
        'IRA ZTE MC8501 5G LIVE SIGNAL CHARTS', 
        html=HTML_CONTENT, 
        js_api=api, 
        width=1100, 
        height=800,
        resizable=True
    )
    webview.start()