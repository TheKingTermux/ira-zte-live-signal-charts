import time
import subprocess
import platform
import requests
import webview
import urllib3

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
        .tab-pane {
            transition: opacity 0.25s ease-in-out, transform 0.25s ease-in-out;
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
        <div id="settingsBox" class="bg-slate-900 border border-slate-800 p-5 rounded-2xl max-w-md w-full mx-4 shadow-2xl space-y-4 text-slate-100 transform scale-95 transition-transform duration-250">
            <div class="flex justify-between items-center pb-2 border-b border-slate-800">
                <h3 class="text-sm font-bold text-cyan-400 flex items-center gap-2">⚙️ Pengaturan & Ping Tool</h3>
                <button onclick="animateButton(this); toggleSettingsModal()" class="text-slate-400 hover:text-white text-xs font-bold px-2 py-1 rounded-lg bg-slate-800">✕</button>
            </div>
            
            <!-- Modal Tabs Header -->
            <div class="flex border-b border-slate-800 text-xs">
                <button onclick="switchTab('tab-general')" id="btn-tab-general" class="flex-1 py-2 font-semibold text-cyan-400 border-b-2 border-cyan-400 bg-cyan-500/10 transition-all duration-300">Pengaturan Umum</button>
                <button onclick="switchTab('tab-ping')" id="btn-tab-ping" class="flex-1 py-2 font-semibold text-slate-400 border-b-2 border-transparent hover:text-slate-200 transition-all duration-300">Ping Tool</button>
            </div>

            <!-- Tab Contents Container (Relative wrapper to prevent layout breaking) -->
            <div class="relative min-h-[170px]">
                <!-- Tab 1: General Settings -->
                <div id="tab-general" class="tab-pane absolute inset-x-0 top-0 space-y-3 pt-1 opacity-100 scale-100">
                    <div>
                        <label class="text-[11px] font-semibold text-slate-300 block mb-1">Tema Tampilan</label>
                        <select id="setting-theme" onchange="changeTheme(this.value)" class="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 p-2 rounded-xl focus:outline-none focus:border-cyan-500 transition-all">
                            <option value="dark" selected>Gelap (Default)</option>
                            <option value="light">Terang</option>
                        </select>
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-300 block mb-1">Frekuensi Update Data (Refresh Rate)</label>
                        <select id="setting-freq" onchange="changeFrequency(this.value)" class="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 p-2 rounded-xl focus:outline-none focus:border-cyan-500 transition-all">
                            <option value="1000" selected>Cepat / Default (1 Detik)</option>
                            <option value="2000">Normal (2 Detik)</option>
                            <option value="4000">Lambat (4 Detik)</option>
                        </select>
                    </div>
                </div>

                <!-- Tab 2: Ping Tool -->
                <div id="tab-ping" class="tab-pane absolute inset-x-0 top-0 space-y-3 pt-1 opacity-0 scale-95 pointer-events-none hidden">
                    <div>
                        <label class="text-[11px] font-semibold text-slate-300 block mb-1">Target Host / IP</label>
                        <div class="flex gap-2">
                            <input type="text" id="ping-host" value="1.1.1.1" class="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 p-2 rounded-xl focus:outline-none focus:border-cyan-500 transition-all">
                            <button onclick="animateButton(this); runPing()" id="btn-ping" class="bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded-xl text-xs font-semibold shrink-0 transition-all active:scale-95">Ping</button>
                        </div>
                    </div>
                    <div>
                        <label class="text-[11px] font-semibold text-slate-300 block mb-1">Hasil Ping</label>
                        <pre id="ping-output" class="w-full bg-slate-950 border border-slate-800 text-[10px] text-emerald-400 p-2.5 rounded-xl h-24 overflow-y-auto font-mono">Menunggu perintah...</pre>
                    </div>
                </div>
            </div>

            <div class="pt-2 flex justify-end border-t border-slate-800 mt-[175px]">
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
        let wasConnected = true;
        let wasInternetOk = true;
        let unreadCount = 0;
        let currentIntervalTime = 1000;
        let pollTimer = null;

        window.addEventListener('DOMContentLoaded', () => {
            loadSettings();
        });

        window.addEventListener('pywebviewready', function() {
            startPolling();
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

        // Clean & Smooth Tab Switcher (No Layout Shifts)
        function switchTab(tabId) {
            const allTabs = ['tab-general', 'tab-ping'];
            const allBtns = ['btn-tab-general', 'btn-tab-ping'];

            allTabs.forEach(id => {
                let pane = document.getElementById(id);
                if (id === tabId) {
                    pane.classList.remove('hidden');
                    void pane.offsetWidth;
                    pane.classList.remove('opacity-0', 'scale-95', 'pointer-events-none');
                    pane.classList.add('opacity-100', 'scale-100');
                } else {
                    pane.classList.remove('opacity-100', 'scale-100');
                    pane.classList.add('opacity-0', 'scale-95', 'pointer-events-none');
                    setTimeout(() => {
                        if (!pane.classList.contains('opacity-100')) {
                            pane.classList.add('hidden');
                        }
                    }, 250);
                }
            });

            allBtns.forEach(id => {
                let btn = document.getElementById(id);
                if (id === 'btn-' + tabId) {
                    btn.className = "flex-1 py-2 font-semibold text-cyan-400 border-b-2 border-cyan-400 bg-cyan-500/10 transition-all duration-300";
                } else {
                    btn.className = "flex-1 py-2 font-semibold text-slate-400 border-b-2 border-transparent hover:text-slate-200 transition-all duration-300";
                }
            });
        }

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

        async function runPing() {
            let host = document.getElementById('ping-host').value.trim();
            let outputEl = document.getElementById('ping-output');
            let btn = event.target;

            if (!host) {
                alert('Masukkan host atau IP tujuan ping!');
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

        function animateButton(btn) {
            btn.style.transform = 'scale(0.9)';
            setTimeout(() => btn.style.transform = 'scale(1)', 150);
        }

        function loadSettings() {
            let savedTheme = localStorage.getItem('router_theme') || 'dark';
            let savedFreq = localStorage.getItem('router_freq') || '1000';

            document.getElementById('setting-theme').value = savedTheme;
            changeTheme(savedTheme, false);

            document.getElementById('setting-freq').value = savedFreq;
            currentIntervalTime = parseInt(savedFreq);
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

        function toggleSettingsModal() {
            let modal = document.getElementById('settingsModal');
            if (modal.classList.contains('pointer-events-none')) {
                openModal('settingsModal', 'settingsBox');
            } else {
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
                    animation: {
                        duration: 300,
                        easing: 'easeOutQuad'
                    },
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

        function updateUI(data) {
            const now = new Date();
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            const seconds = String(now.getSeconds()).padStart(2, '0');
            const nowTime = `${hours}:${minutes}:${seconds}`;

            const signalBar = parseInt(data.signalbar);
            const isConnected = !isNaN(signalBar) && signalBar > 0;
            const internetOk = data.internet_ok !== false;

            const towerStatusEl = document.getElementById('tower-status-val');
            const internetStatusEl = document.getElementById('internet-status-val');
            const floatingAlert = document.getElementById('floating-alert');
            const floatingAlertText = document.getElementById('floating-alert-text');

            if (!isConnected) {
                towerStatusEl.innerText = 'Terputus';
                towerStatusEl.className = 'text-[11px] font-bold text-orange-500 mt-0.5 truncate';
                floatingAlertText.innerText = '⚠️ KONEKSI TOWER TERPUTUS!';
                floatingAlert.classList.remove('hidden');

                if (wasConnected) {
                    addHistoryLog('Tower Terputus', nowTime);
                    wasConnected = false;
                    playAlertSound();
                    document.getElementById('modal-title-disc').innerText = 'KONEKSI TOWER TERPUTUS!';
                    document.getElementById('modal-desc-disc').innerText = 'Sinyal bar terdeteksi 0 atau terputus dari jaringan utama.';
                    openModal('disconnectModal', 'disconnectBox');
                }
            } else if (!internetOk) {
                towerStatusEl.innerText = 'Tersambung';
                towerStatusEl.className = 'text-[11px] font-bold text-emerald-400 mt-0.5 truncate';
                internetStatusEl.innerText = 'Bermasalah';
                internetStatusEl.className = 'text-[11px] font-bold text-orange-500 mt-0.5 truncate';
                
                floatingAlertText.innerText = '🌐 INTERNET BERMASALAH (Tower Aktif, Tidak Ada Akses Internet)!';
                floatingAlert.classList.remove('hidden');

                if (wasInternetOk) {
                    addHistoryLog('Internet Bermasalah', nowTime);
                    wasInternetOk = false;
                    playAlertSound();
                    document.getElementById('modal-title-disc').innerText = 'INTERNET BERMASALAH!';
                    document.getElementById('modal-desc-disc').innerText = 'Status tower tersambung (Signal Bar > 0), tetapi tidak ada koneksi internet yang dapat dijangkau.';
                    openModal('disconnectModal', 'disconnectBox');
                }
            } else {
                towerStatusEl.innerText = 'Tersambung';
                towerStatusEl.className = 'text-[11px] font-bold text-emerald-400 mt-0.5 truncate';
                internetStatusEl.innerText = 'Normal';
                internetStatusEl.className = 'text-[11px] font-bold text-emerald-400 mt-0.5 truncate';
                floatingAlert.classList.add('hidden');
                
                if (!wasConnected || !wasInternetOk) {
                    addHistoryLog('Jaringan Normal Kembali', nowTime);
                    wasConnected = true;
                    wasInternetOk = true;
                    openModal('reconnectModal', 'reconnectBox');
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
                }
            } catch (err) {
                console.error("Gagal ambil data:", err);
                let connEl = document.getElementById('status-conn');
                connEl.innerText = "Terputus...";
                connEl.className = "text-[11px] font-medium bg-red-950/40 border border-red-500/30 text-red-400 px-3 py-1 rounded-xl shadow-inner";
            }
        }
    </script>
</body>
</html>
"""

class Api:
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

        try:
            requests.get("http://1.1.1.1", timeout=1.5)
            internet_ok = True
        except Exception:
            internet_ok = False

        data["internet_ok"] = internet_ok
        return data

    def run_ping(self, host="1.1.1.1"):
        try:
            param = "-n" if platform.system().lower() == "windows" else "-c"
            command = ["ping", param, "4", host]
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True, timeout=10)
            return {"success": True, "output": output}
        except Exception as e:
            return {"success": False, "output": str(e)}

if __name__ == '__main__':
    api = Api()
    window = webview.create_window(
        'IRA ZTE MC8501 5G LIVE SIGNAL CHARTS', 
        html=HTML_CONTENT, 
        js_api=api, 
        width=1100, 
        height=750,
        resizable=True
    )
    webview.start()