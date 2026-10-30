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
SPEED_TEST_ENDPOINT = "https://speed.cloudflare.com"
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
        /* Subtle dropdown interaction; native option menus remain OS-rendered. */
        select { transform-origin: top center; transition: border-color 180ms ease, box-shadow 180ms ease, transform 180ms ease, background-color 180ms ease; }
        select:focus { transform: translateY(-1px); box-shadow: 0 0 0 2px rgb(34 211 238 / 12%); }
        select option { background: #020617; color: #e2e8f0; }
        .bell-arrival { animation: bell-arrival 700ms cubic-bezier(.2,.8,.2,1); }
        @keyframes bell-arrival {
            0% { transform: rotate(0) scale(1); filter: drop-shadow(0 0 0 rgb(248 113 113 / 0)); }
            18% { transform: rotate(-18deg) scale(1.12); }
            36% { transform: rotate(16deg) scale(1.16); filter: drop-shadow(0 0 8px rgb(248 113 113 / 75%)); }
            54% { transform: rotate(-10deg) scale(1.08); }
            72% { transform: rotate(7deg) scale(1.03); }
            100% { transform: rotate(0) scale(1); filter: drop-shadow(0 0 0 rgb(248 113 113 / 0)); }
        }
        @media (prefers-reduced-motion: reduce) { select { transition: none; } .bell-arrival { animation: none !important; } }

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
        /* Mode terang: kartu tetap gelap (hampir solid) agar semua nilai terbaca;
           elemen yang langsung berada di atas latar terang diberi warna gelap. */
        .theme-light #app-title { color: #0e7490; }
        .theme-light #app-subtitle { color: #475569; }
        .theme-light .card-bg { background-color: rgb(15 23 42 / 0.96); }
        .theme-light #status-conn { background-color: #0f172a !important; border-color: #1e293b !important; }
        /* ===== Transisi tema gelap <-> terang ===== */
        body.theme-light { background-color: #f1f5f9; color: #0f172a; }
        ::view-transition-old(root), ::view-transition-new(root) { animation: none; mix-blend-mode: normal; }
        ::view-transition-old(root) { z-index: 1; }
        ::view-transition-new(root) { z-index: 2; }
        html.theme-vt *, html.theme-vt *::before, html.theme-vt *::after { transition: none !important; }
        html.theme-animating, html.theme-animating *, html.theme-animating *::before, html.theme-animating *::after {
            transition: background-color 0.7s cubic-bezier(0.4, 0, 0.2, 1), color 0.7s cubic-bezier(0.4, 0, 0.2, 1),
                        border-color 0.7s cubic-bezier(0.4, 0, 0.2, 1), fill 0.7s ease, stroke 0.7s ease, box-shadow 0.7s ease !important;
        }
        /* ===== Splash screen ===== */
        #splash {
            position: fixed; inset: 0; z-index: 200; display: flex; flex-direction: column;
            align-items: center; justify-content: center; gap: 16px; overflow: hidden; color: #e2e8f0;
            background: radial-gradient(circle at 50% 42%, #0b2a55 0%, #06122b 45%, #020617 100%);
            transition: opacity 0.55s ease, transform 0.55s ease, visibility 0.55s;
        }
        #splash.splash-hide { opacity: 0; transform: scale(1.04); visibility: hidden; pointer-events: none; }
        #splash .splash-grid {
            position: absolute; inset: 0; opacity: 0.9;
            background-image: linear-gradient(rgba(56,189,248,0.07) 1px, transparent 1px), linear-gradient(90deg, rgba(56,189,248,0.07) 1px, transparent 1px);
            background-size: 38px 38px;
            -webkit-mask-image: radial-gradient(circle at 50% 45%, #000 0%, transparent 72%);
            mask-image: radial-gradient(circle at 50% 45%, #000 0%, transparent 72%);
            animation: splashGrid 14s linear infinite;
        }
        #splash .splash-title {
            position: relative; font-size: 44px; line-height: 1; font-weight: 900; letter-spacing: 0.18em; padding-left: 0.18em;
            background: linear-gradient(180deg, #ffffff 10%, #7dd3fc 60%, #22d3ee 100%);
            -webkit-background-clip: text; background-clip: text; color: transparent;
            filter: drop-shadow(0 0 18px rgba(34,211,238,0.45));
            animation: splashTitle 0.9s cubic-bezier(0.2, 0.8, 0.2, 1) both;
        }
        #splash .splash-sub {
            position: relative; margin-top: -6px; font-size: 13px; font-weight: 700; letter-spacing: 0.42em; padding-left: 0.42em;
            text-transform: uppercase; color: #93c5fd; animation: splashRise 0.8s 0.35s cubic-bezier(0.2, 0.8, 0.2, 1) both;
        }
        #splash .splash-logo-wrap {
            position: relative; width: 168px; height: 168px; margin-top: 10px; opacity: 0;
            animation: splashLogo 0.85s 1s cubic-bezier(0.2, 0.9, 0.25, 1.15) forwards;
        }
        #splash .splash-logo {
            position: relative; width: 100%; height: 100%; border-radius: 26px; display: block;
            box-shadow: 0 0 36px rgba(34,211,238,0.5), 0 0 90px rgba(37,99,235,0.4);
            animation: splashFloat 3.4s ease-in-out 1.9s infinite;
        }
        #splash .splash-ring {
            position: absolute; inset: -12px; border-radius: 34px; border: 2px solid rgba(34,211,238,0.6); opacity: 0;
            animation: splashRing 2.4s ease-out 1.5s infinite;
        }
        #splash .splash-ring + .splash-ring { animation-delay: 2.7s; }
        #splash .splash-bars { position: relative; display: flex; gap: 5px; align-items: flex-end; height: 22px; opacity: 0; animation: splashRise 0.6s 1.3s both; }
        #splash .splash-bars span {
            width: 5px; border-radius: 2px; background: linear-gradient(#22d3ee, #2563eb);
            transform-origin: bottom; animation: splashBar 1s ease-in-out infinite;
        }
        #splash .splash-progress { position: relative; width: 210px; height: 3px; border-radius: 999px; background: rgba(148,163,184,0.22); overflow: hidden; opacity: 0; animation: splashRise 0.5s 1.2s both; }
        #splash .splash-progress i {
            display: block; height: 100%; width: 0; border-radius: 999px; background: linear-gradient(90deg, #22d3ee, #3b82f6);
            animation: splashFill var(--splash-hold, 3s) linear 1s forwards;
        }
        #splash .splash-loading { position: relative; font-size: 10px; letter-spacing: 0.3em; padding-left: 0.3em; color: #64748b; opacity: 0; animation: splashRise 0.6s 1.3s both; }
        #splash.splash-static .splash-title, #splash.splash-static .splash-sub, #splash.splash-static .splash-logo-wrap,
        #splash.splash-static .splash-bars, #splash.splash-static .splash-progress, #splash.splash-static .splash-loading {
            animation: none; opacity: 1; transform: none;
        }
        #splash.splash-static .splash-grid, #splash.splash-static .splash-logo, #splash.splash-static .splash-ring,
        #splash.splash-static .splash-bars span { animation: none; }
        #splash.splash-static .splash-ring { display: none; }
        #splash.splash-static .splash-progress i { animation: none; width: 100%; }
        @keyframes splashTitle { from { opacity: 0; letter-spacing: 0.55em; transform: translateY(-10px); } to { opacity: 1; letter-spacing: 0.18em; transform: none; } }
        @keyframes splashRise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
        @keyframes splashLogo { from { opacity: 0; transform: scale(0.6) rotate(-6deg); } to { opacity: 1; transform: scale(1) rotate(0); } }
        @keyframes splashFloat { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }
        @keyframes splashRing { 0% { opacity: 0.7; transform: scale(0.96); } 100% { opacity: 0; transform: scale(1.45); } }
        @keyframes splashBar { 0%, 100% { transform: scaleY(0.35); } 50% { transform: scaleY(1); } }
        @keyframes splashFill { from { width: 0; } to { width: 100%; } }
        @keyframes splashGrid { from { background-position: 0 0; } to { background-position: 38px 38px; } }
    </style>
</head>
<body id="app-body" class="bg-slate-950 text-slate-100 h-screen overflow-hidden p-4 flex flex-col justify-between select-none relative">
    <div class="hidden bg-slate-100 text-slate-900" aria-hidden="true"></div>
    <div id="splash" role="status" aria-live="polite" aria-label="Memuat IRA ZTE Live Signal Charts">
        <div class="splash-grid"></div>
        <div class="splash-title">IRA ZTE</div>
        <div class="splash-sub">Live Signal Charts</div>
        <div class="splash-logo-wrap">
            <span class="splash-ring"></span><span class="splash-ring"></span>
            <img class="splash-logo" alt="Logo IRA ZTE" src="data:image/png;base64,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">
        </div>
        <div class="splash-bars" aria-hidden="true">
            <span style="height:8px;animation-delay:0s"></span><span style="height:12px;animation-delay:0.12s"></span>
            <span style="height:16px;animation-delay:0.24s"></span><span style="height:20px;animation-delay:0.36s"></span>
            <span style="height:14px;animation-delay:0.48s"></span>
        </div>
        <div class="splash-progress" aria-hidden="true"><i></i></div>
        <div class="splash-loading">MEMUAT DASHBOARD</div>
    </div>
    
    <!-- Header -->
    <header class="flex justify-between items-center pb-2 border-b border-slate-800 gap-2 shrink-0 relative">
        <div>
            <h1 id="app-title" class="text-lg font-black tracking-wider text-cyan-400 flex items-center gap-2">
                <span class="relative flex h-2.5 w-2.5">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
                </span>
                IRA ZTE MC8501 5G LIVE SIGNAL CHARTS
            </h1>
            <p id="app-subtitle" class="text-[10px] text-slate-400">Real-time Telemetry & Smart Network Diagnostic Dashboard</p>
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
                        <div id="status-rsrp" class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[10px] font-semibold text-slate-300">
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
                        <div id="status-rssi" class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[10px] font-semibold text-slate-300">
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
                        <div id="status-rsrq" class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[10px] font-semibold text-slate-300">
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
                        <div id="status-sinr" class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[10px] font-semibold text-slate-300">
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
                        <div id="status-ping" class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-[10px] font-semibold text-slate-300">
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
            <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
                
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
                    <div class="text-[9px] uppercase font-semibold text-slate-400">NR-ARFCN 5G</div>
                    <div id="info-arfcn" class="text-[11px] font-bold text-slate-100 mt-0.5">-</div>
                    <div id="info-arfcn-freq" class="text-[9px] text-slate-400 leading-tight">-</div>
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
                        <div class="text-[11px] font-semibold text-slate-300">Pop-up Gangguan Jaringan</div>
                        <label class="flex items-center gap-2 text-[11px] text-slate-300">
                            <input id="suppress-tower-popup" type="checkbox" onchange="savePopupPreferences()" class="accent-cyan-500">
                            Sembunyikan pop-up saat tower bermasalah
                        </label>
                        <label class="flex items-center gap-2 text-[11px] text-slate-300">
                            <input id="suppress-internet-popup" type="checkbox" onchange="savePopupPreferences()" class="accent-cyan-500">
                            Sembunyikan pop-up saat internet bermasalah
                        </label>
                        <button onclick="animateButton(this); resetPopupPreferences()" class="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-semibold px-3 py-2 rounded-lg transition-all">Reset Notifikasi Gangguan</button>
                        <p class="text-[10px] text-slate-500">Pop-up gangguan tampil secara default. Banner, suara, dan riwayat tetap aktif walau pop-up disembunyikan. Reset menampilkan kembali pop-up gangguan tower dan internet.</p>
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
                    <div id="startup-setting" class="hidden rounded-xl border border-slate-800 bg-slate-950/50 p-3">
                        <label class="flex items-center gap-2 text-[11px] text-slate-300 cursor-pointer select-none">
                            <input id="setting-startup" type="checkbox" onchange="changeStartup(this.checked)" class="accent-cyan-500">
                            Jalankan aplikasi saat Windows dimulai
                        </label>
                        <p id="startup-status" class="text-[10px] text-slate-500 mt-1">Hanya tersedia untuk aplikasi hasil instalasi.</p>
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
                            <div id="speed-latency-status" class="text-[9px] text-slate-500">Rata-rata latency</div>
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
                    <button onclick="exportDiagnosticLogs()" class="w-full bg-cyan-700 hover:bg-cyan-600 text-white text-xs font-bold px-3 py-2 rounded-xl">📄 Ekspor Log Debug</button>
                    <p id="export-status" class="text-[10px] text-slate-400 min-h-[14px] break-all"></p>
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
                        <p class="text-[10px] text-slate-400">Pilih kanal Stable untuk rilis reguler atau Beta untuk versi pre-release. Jika pemeriksaan otomatis aktif, aplikasi hanya memeriksa update saat dibuka lalu menampilkan pop-up pilihan (Download, Lewati versi ini, atau, khusus versi beta, Jangan tampilkan lagi). Aplikasi tidak pernah mengunduh update sendiri.</p>
                        <div>
                            <label class="text-[10px] text-slate-400 block mb-1">Saluran rilis</label>
                            <select id="setting-update-channel" onchange="saveUpdatePreferences(); runUpdateCheck(false)" class="w-full bg-slate-950 border border-slate-800 text-xs text-slate-200 p-2 rounded-xl focus:outline-none focus:border-cyan-500">
                                <option value="stable">Stable — rilis resmi</option>
                                <option value="beta">Beta — pre-release</option>
                            </select>
                        </div>
                        <label class="flex items-center gap-2 text-[11px] text-slate-300">
                            <input id="setting-auto-update-check" type="checkbox" onchange="saveUpdatePreferences()" class="accent-cyan-500">
                            Periksa update otomatis saat aplikasi dibuka (tanpa unduh otomatis)
                        </label>
                        <div class="flex flex-col sm:flex-row gap-2">
                            <button id="btn-check-update" onclick="runUpdateCheck(true)" class="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-[10px] font-semibold px-3 py-2 rounded-lg">🔎 Periksa Update</button>
                            <button onclick="resetUpdatePreferences()" class="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-200 text-[10px] font-semibold px-3 py-2 rounded-lg">↺ Reset update yang disembunyikan</button>
                        </div>
                        <p id="update-status" class="text-[10px] text-slate-400">Belum memeriksa update.</p>
                        <div class="border-t border-slate-800 pt-3">
                            <div class="text-[11px] font-bold text-cyan-300 mb-1">Informasi Release</div>
                            <p id="about-update-details" class="text-[10px] text-slate-400">Belum ada informasi release.</p>
                            <div id="release-notes" class="hidden mt-2"></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="pt-3 flex justify-end border-t border-slate-800 mt-3 shrink-0 bg-slate-900">
                <button onclick="animateButton(this); toggleSettingsModal()" class="w-full bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-semibold py-2.5 rounded-xl shadow-lg transition-all active:scale-95">Tutup</button>
            </div>
        </div>
    </div>

    <!-- Update Modal: pilih Download / Lewati versi ini / Jangan tampilkan lagi -->
    <div id="updateModal" class="fixed inset-0 z-[60] flex items-center justify-center bg-slate-950/80 backdrop-blur-sm opacity-0 pointer-events-none modal-transition">
        <div id="updateBox" class="bg-slate-900 border border-cyan-500/40 p-5 rounded-2xl max-w-md w-full mx-4 max-h-[94vh] overflow-y-auto shadow-2xl shadow-cyan-500/10 text-slate-100 transform scale-95 transition-transform duration-200">
            <div class="flex items-start gap-3 pb-3 border-b border-slate-800 mb-3">
                <div id="um-icon" class="text-3xl leading-none">⬆️</div>
                <div class="min-w-0 flex-1">
                    <h3 id="um-title" class="text-sm font-bold text-cyan-300">Pembaruan Aplikasi</h3>
                    <p id="um-subtitle" class="text-[11px] text-slate-400"></p>
                </div>
            </div>

            <div id="um-checking" class="hidden text-center py-6 space-y-3">
                <div class="mx-auto h-8 w-8 rounded-full border-2 border-slate-700 border-t-cyan-400 animate-spin"></div>
                <p class="text-xs text-slate-300">Memeriksa update di GitHub…</p>
            </div>

            <div id="um-available" class="hidden space-y-3">
                <div class="grid grid-cols-2 gap-2 text-[11px]">
                    <div class="rounded-lg bg-slate-950/60 border border-slate-800 p-2"><div class="text-[9px] uppercase font-semibold text-slate-500">Versi terpasang</div><div id="um-current" class="font-bold text-slate-200 break-all">-</div></div>
                    <div class="rounded-lg bg-slate-950/60 border border-emerald-500/30 p-2"><div class="text-[9px] uppercase font-semibold text-slate-500">Versi update</div><div id="um-latest" class="font-bold text-emerald-300 break-all">-</div></div>
                    <div class="rounded-lg bg-slate-950/60 border border-slate-800 p-2"><div class="text-[9px] uppercase font-semibold text-slate-500">Ukuran update</div><div id="um-size" class="font-bold text-slate-200">-</div></div>
                    <div class="rounded-lg bg-slate-950/60 border border-slate-800 p-2"><div class="text-[9px] uppercase font-semibold text-slate-500">Kanal</div><div id="um-channel" class="font-bold text-slate-200">-</div></div>
                </div>
                <div id="um-notes" class="hidden max-h-[26vh] overflow-y-auto pr-1"></div>
                <div class="space-y-2">
                    <button id="um-btn-download" onclick="startUpdateDownload()" class="w-full bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold px-4 py-2.5 rounded-xl transition-all active:scale-95">⬇ Download &amp; Pasang</button>
                    <div class="grid grid-cols-2 gap-2">
                        <button id="um-btn-skip" onclick="skipUpdateVersion()" class="bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-semibold px-3 py-2 rounded-xl transition-all active:scale-95">⏭ Lewati versi ini</button>
                        <button id="um-btn-hide" onclick="hideUpdateSeries()" class="bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px] font-semibold px-3 py-2 rounded-xl transition-all active:scale-95">🚫 Jangan tampilkan lagi (beta)</button>
                    </div>
                    <p id="um-hide-hint" class="text-[10px] text-slate-500 text-center leading-snug"></p>
                    <button onclick="closeUpdateModal()" class="w-full text-[11px] text-slate-400 hover:text-slate-200 py-1">Nanti saja</button>
                </div>
            </div>

            <div id="um-downloading" class="hidden space-y-3">
                <div class="flex justify-between gap-2 text-[11px]"><span id="um-dl-status" class="text-slate-300">Menyiapkan unduhan…</span><span id="um-dl-percent" class="font-bold text-cyan-300">0%</span></div>
                <div class="h-2.5 overflow-hidden rounded-full bg-slate-800"><div id="um-dl-bar" class="h-full w-0 rounded-full bg-gradient-to-r from-cyan-500 to-emerald-400 transition-[width] duration-200"></div></div>
                <div class="grid grid-cols-2 gap-2 text-[11px]">
                    <div class="rounded-lg bg-slate-950/60 border border-slate-800 p-2"><div class="text-[9px] uppercase font-semibold text-slate-500">Versi update</div><div id="um-dl-version" class="font-bold text-emerald-300 break-all">-</div></div>
                    <div class="rounded-lg bg-slate-950/60 border border-slate-800 p-2"><div class="text-[9px] uppercase font-semibold text-slate-500">Ukuran</div><div id="um-dl-size" class="font-bold text-slate-200">-</div></div>
                    <div class="rounded-lg bg-slate-950/60 border border-slate-800 p-2"><div class="text-[9px] uppercase font-semibold text-slate-500">Kecepatan</div><div id="um-dl-speed" class="font-bold text-slate-200">-</div></div>
                    <div class="rounded-lg bg-slate-950/60 border border-slate-800 p-2"><div class="text-[9px] uppercase font-semibold text-slate-500">Perkiraan selesai</div><div id="um-dl-eta" class="font-bold text-slate-200">-</div></div>
                </div>
                <p id="um-dl-note" class="text-[10px] text-slate-500 text-center leading-snug">Jangan tutup aplikasi selama unduhan berlangsung.</p>
                <button id="um-dl-close" onclick="closeUpdateModal()" class="hidden w-full bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-3 py-2 rounded-xl">Tutup</button>
            </div>

            <div id="um-none" class="hidden text-center py-3 space-y-3">
                <p id="um-none-text" class="text-xs text-slate-300 leading-relaxed">Tidak ada update. Aplikasi sudah menggunakan versi terbaru.</p>
                <button onclick="closeUpdateModal()" class="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-3 py-2 rounded-xl">Tutup</button>
            </div>

            <div id="um-error" class="hidden text-center py-3 space-y-3">
                <p id="um-error-text" class="text-xs text-orange-300 leading-relaxed break-words">Terjadi kesalahan.</p>
                <div class="grid grid-cols-2 gap-2">
                    <button id="um-btn-retry" onclick="retryUpdateAction()" class="bg-cyan-700 hover:bg-cyan-600 text-white text-xs font-semibold px-3 py-2 rounded-xl">Coba lagi</button>
                    <button onclick="closeUpdateModal()" class="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold px-3 py-2 rounded-xl">Tutup</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Disconnected Alert Popup Modal (Animated with Recheck Button) -->
    <div id="disconnectModal" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 backdrop-blur-sm opacity-0 pointer-events-none modal-transition">
        <div id="disconnectBox" class="bg-slate-900 border-2 border-orange-500/80 p-6 rounded-2xl max-w-md w-full mx-4 max-h-[94vh] overflow-y-auto shadow-2xl shadow-orange-500/20 text-slate-100 transform scale-95 transition-transform duration-250">
            <div class="w-12 h-12 bg-orange-500/10 text-orange-500 rounded-xl flex items-center justify-center mx-auto mb-3 text-2xl font-bold animate-bounce">⚠️</div>
            <h3 id="modal-title-disc" class="text-lg font-bold text-orange-400 text-center mb-1">KONEKSI TOWER TERPUTUS!</h3>
            <p id="modal-desc-disc" class="text-xs text-slate-300 text-center mb-1">Sinyal bar terdeteksi 0 atau terputus dari jaringan utama.</p>
            <p id="disc-elapsed" class="text-[10px] text-slate-500 text-center mb-2"></p>
            <div id="disc-details" class="max-h-[34vh] overflow-y-auto pr-1 mb-3 text-left"></div>
            <label class="flex items-center justify-center gap-2 text-[11px] text-slate-300 mb-3 cursor-pointer select-none">
                <input id="disc-suppress-checkbox" type="checkbox" onchange="onIssuePopupSuppressChange(this.checked)" class="accent-cyan-500">
                Jangan tampilkan pop-up ini lagi
            </label>
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
        // Akses penyimpanan yang aman: localStorage bisa melempar SecurityError
        // di WebView (halaman dari string HTML). Tanpa ini satu error saja
        // menghentikan inisialisasi dan status terus "Menghubungkan...".
        const safeStorage = (function() {
            const mem = {};
            let ok = false;
            try {
                window.localStorage.setItem('__probe__', '1');
                window.localStorage.removeItem('__probe__');
                ok = true;
            } catch (e) { ok = false; }
            return {
                getItem: function(k) {
                    if (ok) { try { return window.localStorage.getItem(k); } catch (e) {} }
                    return Object.prototype.hasOwnProperty.call(mem, k) ? mem[k] : null;
                },
                setItem: function(k, v) {
                    mem[k] = String(v);
                    if (ok) { try { window.localStorage.setItem(k, String(v)); } catch (e) {} }
                },
                removeItem: function(k) {
                    delete mem[k];
                    if (ok) { try { window.localStorage.removeItem(k); } catch (e) {} }
                }
            };
        })();

        // ===== Splash screen: judul -> logo IRA -> jeda 3 detik -> dashboard dimuat =====
        // Diletakkan di awal skrip agar tetap berjalan walau kode lain gagal; timer-nya tidak
        // bergantung pada kode lain sehingga splash tidak mungkin menutupi dashboard selamanya.
        const SPLASH_LOGO_AT_MS = 1000;   // logo muncul setelah judul
        const SPLASH_HOLD_MS = 3000;      // jeda setelah logo muncul, baru dashboard dimuat
        const SPLASH_FADE_MS = 550;
        let splashFinished = false;
        const splashWaiters = [];

        function whenSplashDone(callback) {
            if (splashFinished) { callback(); return; }
            splashWaiters.push(callback);
        }

        function finishSplash() {
            if (splashFinished) return;
            splashFinished = true;
            try { window.sessionStorage.setItem('ira_splash_seen', '1'); } catch (error) { /* diabaikan */ }
            const splash = document.getElementById('splash');
            if (splash) {
                splash.classList.add('splash-hide');
                setTimeout(() => { if (splash.parentNode) splash.parentNode.removeChild(splash); }, SPLASH_FADE_MS + 150);
            }
            splashWaiters.splice(0).forEach(callback => {
                try { callback(); } catch (error) { console.error('Callback setelah splash gagal:', error); }
            });
        }

        function startSplash() {
            const splash = document.getElementById('splash');
            if (!splash) { finishSplash(); return; }
            let seen = false;
            try { seen = window.sessionStorage.getItem('ira_splash_seen') === '1'; } catch (error) { /* diabaikan */ }
            // Halaman dimuat ulang dalam sesi yang sama (mis. Android memulihkan aplikasi): lewati splash.
            if (seen) { splash.style.transition = 'none'; finishSplash(); return; }
            const reduceMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
            if (reduceMotion) splash.classList.add('splash-static');
            splash.style.setProperty('--splash-hold', (SPLASH_HOLD_MS / 1000) + 's');
            setTimeout(finishSplash, reduceMotion ? 1500 : SPLASH_LOGO_AT_MS + SPLASH_HOLD_MS);
        }

        startSplash();

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

        let pywebviewInitialized = false;

        function initializeDesktopBridge() {
            if (pywebviewInitialized || !window.pywebview || !window.pywebview.api) return;
            pywebviewInitialized = true;
            try {
            const pingFreqSelect = document.getElementById('setting-ping-freq');
            const savedPingFreq = safeStorage.getItem('router_ping_freq');
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
                    safeStorage.setItem('router_ping_freq', 'auto');
                    updatePingMonitorFrequency(false);
                }
            }
            } catch (error) {
                console.error('Gagal memuat pengaturan ping:', error);
            }
            loadStartupSetting();
            // Telemetri dimuat setelah splash selesai (judul -> logo -> jeda -> dashboard).
            whenSplashDone(() => {
                startPolling();
                startPingMonitor();
            });
        }

        // The ready event can fire before this listener is attached in some WebView
        // startup paths. Check the bridge as well, so desktop polling cannot remain
        // forever on the initial "Menghubungkan..." state.
        window.addEventListener('pywebviewready', initializeDesktopBridge);
        document.addEventListener('DOMContentLoaded', () => {
            initializeDesktopBridge();
            let bridgeChecks = 0;
            const checkBridge = () => {
                if (pywebviewInitialized || bridgeChecks++ >= 30) return;
                initializeDesktopBridge();
                if (!pywebviewInitialized) setTimeout(checkBridge, 250);
            };
            checkBridge();
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
            let elapsedTimer = null;
            try {
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

            elapsedTimer = setInterval(() => {
                const elapsed = (performance.now() - started) / 1000;
                document.getElementById('speed-elapsed').innerText = elapsed.toFixed(1) + ' / 90 detik';
            }, 100);

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
                if (elapsedTimer) clearInterval(elapsedTimer);
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
            const savedTheme = safeStorage.getItem('router_theme') || 'dark';
            const allowedFrequencies = ['1000', '2000', '4000'];
            const storedFreq = safeStorage.getItem('router_freq') || '1000';
            const savedFreq = allowedFrequencies.includes(storedFreq) ? storedFreq : '1000';

            document.getElementById('setting-theme').value = savedTheme;
            changeTheme(savedTheme, false);
            document.getElementById('setting-freq').value = savedFreq;
            currentIntervalTime = Number.parseInt(savedFreq, 10);
            document.getElementById('suppress-tower-popup').checked = safeStorage.getItem('suppress_tower_popup') === 'true';
            document.getElementById('suppress-internet-popup').checked = safeStorage.getItem('suppress_internet_popup') === 'true';
            const updateChannel = safeStorage.getItem('update_channel') === 'beta' ? 'beta' : 'stable';
            document.getElementById('setting-update-channel').value = updateChannel;
            document.getElementById('setting-auto-update-check').checked = safeStorage.getItem('auto_update_check') !== 'false';
            document.getElementById('about-app-version').innerText = APP_VERSION_JS;
            scheduleAutoUpdateChecks();
        }

        const APP_VERSION_JS = "__APP_VERSION__";
        // ===== Catatan rilis: Baru / Perbaikan / Perubahan / Lainnya =====
        const RELEASE_GROUPS = [
            { key: 'new', icon: '✨', title: 'Baru (New)', cls: 'text-emerald-300' },
            { key: 'fix', icon: '🐛', title: 'Perbaikan (Fix)', cls: 'text-orange-300' },
            { key: 'changed', icon: '🔄', title: 'Perubahan (Changed)', cls: 'text-cyan-300' },
            { key: 'other', icon: '🔧', title: 'Lainnya', cls: 'text-slate-300' }
        ];
        const RELEASE_TYPE_MAP = {
            feat: 'new', feature: 'new', add: 'new', new: 'new',
            fix: 'fix', bugfix: 'fix', hotfix: 'fix',
            perf: 'changed', refactor: 'changed', style: 'changed', update: 'changed', change: 'changed', improve: 'changed',
            docs: 'other', chore: 'other', ci: 'other', build: 'other', test: 'other', deps: 'other', revert: 'other', release: 'other', bump: 'other'
        };

        function releaseHeadingKey(title) {
            const t = String(title).toLowerCase().replace(/[^a-z\\s']/g, ' ').replace(/\\s+/g, ' ').trim();
            if (/what'?s changed|changelog|ringkasan|summary/.test(t)) return null;
            if (/\\b(new|feature|features|baru|fitur)\\b/.test(t)) return 'new';
            if (/\\b(fix|fixes|fixed|bug|bugs|perbaikan|perbaiki)\\b/.test(t)) return 'fix';
            if (/\\b(changed|change|changes|perubahan|improve|improvement|improvements|update)\\b/.test(t)) return 'changed';
            if (/\\b(other|others|lainnya|maintenance|pemeliharaan|chore|docs)\\b/.test(t)) return 'other';
            return null;
        }

        function parseReleaseNotes(body) {
            const result = { groups: { new: [], fix: [], changed: [], other: [] }, intro: [], changelogUrl: null, since: null, total: 0 };
            const lines = String(body || '').replace(/\\r\\n?/g, '\\n').split('\\n');
            let headingKey = null;

            const addItem = (rawText) => {
                let text = rawText.replace(/\\[([^\\]]+)\\]\\([^)]*\\)/g, '$1').replace(/`/g, '').replace(/\\*\\*/g, '').trim();
                let author = null, ref = null;
                const by = text.match(/^(.*?)\\s+by\\s+@([\\w-]+)\\s+in\\s+(https?:\\/\\/\\S+)\\s*$/);
                if (by) {
                    text = by[1].trim();
                    author = by[2];
                    const pr = by[3].match(/\\/pull\\/(\\d+)/);
                    if (pr) ref = '#' + pr[1];
                }
                const sha = text.match(/\\s*\\(([0-9a-f]{7,10})\\)\\s*$/);
                if (sha) {
                    text = text.slice(0, sha.index).trim();
                    if (!ref) ref = sha[1];
                }
                if (!text || /^merge\\b/i.test(text) || /stamp build version/i.test(text) || /^automated\\b/i.test(text)) return;

                let key = headingKey;
                const prefix = text.match(/^(\\w+)(?:\\([^)]*\\))?!?:\\s*(.*)$/);
                if (prefix) {
                    const typed = RELEASE_TYPE_MAP[prefix[1].toLowerCase()];
                    if (typed) {
                        if (!key) key = typed;
                        text = prefix[2].trim();
                    }
                }
                if (!key) {
                    const first = (text.split(/\\s+/)[0] || '').toLowerCase();
                    if (/^(fix|fixed|fixes|perbaiki|perbaikan|bugfix)$/.test(first)) key = 'fix';
                    else if (/^(add|added|new|tambah|tambahkan|baru)$/.test(first)) key = 'new';
                    else key = 'changed';
                }
                if (!text) return;
                text = text.charAt(0).toUpperCase() + text.slice(1);
                result.groups[key].push({ text: text, author: author, ref: ref });
                result.total++;
            };

            lines.forEach(raw => {
                const line = raw.trim();
                if (!line) return;
                const full = line.match(/Full Changelog\\*{0,2}:?\\s*(https?:\\/\\/\\S+)/i);
                if (full) { result.changelogUrl = full[1]; return; }
                const heading = line.match(/^#{1,6}\\s*(.+)$/);
                if (heading) { headingKey = releaseHeadingKey(heading[1]); return; }
                const bullet = line.match(/^[*+-]\\s+(.*)$/);
                if (bullet) { addItem(bullet[1]); return; }
                const since = line.match(/Changes since\\s+(\\S+?)\\.?$/i);
                if (since) { result.since = since[1]; return; }
                result.intro.push(line);
            });
            return result;
        }

        function openExternalLink(url) {
            // Tautan harus dibuka di peramban sistem, bukan menggantikan isi jendela aplikasi.
            try {
                if (window.AndroidBridge && typeof window.AndroidBridge.openUrl === 'function') { window.AndroidBridge.openUrl(url); return false; }
                if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.open_url === 'function') { window.pywebview.api.open_url(url); return false; }
            } catch (error) { console.error('Gagal membuka tautan:', error); }
            return true;
        }

        function rnEl(tag, className, text) {
            const node = document.createElement(tag);
            if (className) node.className = className;
            if (text !== undefined && text !== null) node.textContent = text;
            return node;
        }

        function formatReleaseDate(iso) {
            if (!iso) return '';
            try {
                return new Date(iso).toLocaleString('id-ID', { timeZone: 'Asia/Jakarta', dateStyle: 'medium', timeStyle: 'short' }) + ' WIB';
            } catch (error) { return ''; }
        }

        // Semua teks dari rilis dimasukkan lewat textContent (bukan innerHTML) agar aman dari injeksi HTML.
        function renderReleaseNotes(containerId, info) {
            const box = document.getElementById(containerId);
            if (!box) return;
            box.textContent = '';
            if (!info || !(info.tag_name || info.name)) { box.classList.add('hidden'); return; }
            box.classList.remove('hidden');
            const parsed = parseReleaseNotes(info.body);

            const wrap = rnEl('div', 'rounded-lg border border-slate-800 bg-slate-950/60 p-2 space-y-2');
            wrap.appendChild(rnEl('div', 'text-[11px] font-bold text-cyan-300', '📋 Catatan Rilis ' + (info.name || info.tag_name)));
            const meta = [];
            if (info.channel) meta.push(info.channel === 'beta' ? 'Beta' : 'Stable');
            const when = formatReleaseDate(info.published_at);
            if (when) meta.push(when);
            if (parsed.since) meta.push('perubahan sejak ' + parsed.since);
            if (meta.length) wrap.appendChild(rnEl('div', 'text-[10px] text-slate-500', meta.join(' · ')));

            if (parsed.total === 0) {
                const intro = parsed.intro.filter(line => !/^automated\\b/i.test(line)).join(' ').trim();
                wrap.appendChild(rnEl('div', 'text-[10px] text-slate-400', intro ? intro.slice(0, 400) : 'Rilis ini tidak mencantumkan rincian perubahan.'));
            } else {
                let shown = 0;
                RELEASE_GROUPS.forEach(group => {
                    const items = parsed.groups[group.key];
                    if (!items.length) return;
                    const section = rnEl('div', 'space-y-1');
                    section.appendChild(rnEl('div', 'text-[10px] font-bold uppercase tracking-wider ' + group.cls, group.icon + ' ' + group.title + ' · ' + items.length));
                    const list = rnEl('ul', 'list-disc pl-4 space-y-0.5 text-[10px] text-slate-300');
                    items.forEach(item => {
                        if (shown >= 60) return;
                        shown++;
                        const li = rnEl('li', '', item.text);
                        if (item.ref) li.appendChild(rnEl('span', 'text-slate-500', ' ' + item.ref));
                        list.appendChild(li);
                    });
                    section.appendChild(list);
                    wrap.appendChild(section);
                });
                if (parsed.total > shown) wrap.appendChild(rnEl('div', 'text-[10px] text-slate-500', '…dan ' + (parsed.total - shown) + ' perubahan lainnya.'));
            }

            const link = info.html_url || parsed.changelogUrl;
            if (link) {
                const button = rnEl('button', 'w-full bg-slate-800 hover:bg-slate-700 text-slate-200 text-[10px] font-semibold px-3 py-1.5 rounded-lg', 'Lihat selengkapnya di GitHub');
                button.onclick = () => { openExternalLink(link); };
                wrap.appendChild(button);
            }
            box.appendChild(wrap);
        }

        // ===== Modal update: Download / Lewati versi ini / Jangan tampilkan lagi =====
        // Pemeriksaan otomatis HANYA menampilkan modal (tidak pernah mengunduh sendiri).
        // Pemeriksaan manual dari Pengaturan selalu membuka modal ini, mengabaikan "lewati/sembunyikan".
        const UM_STATES = ['checking', 'available', 'downloading', 'none', 'error'];
        let umInfo = null;
        let umChecking = false;
        let umDownloading = false;
        let umRetryAction = 'check';
        let umAutoShownTag = null;

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

        // "1.1-dev.8" -> "1.1": menyembunyikan satu seri beta berarti update beta 1.1 berikutnya (dev.9, dev.10, ...) ikut
        // hilang. Rilis stabil 1.1 TIDAK ikut tersembunyi.
        function updateSeries(tag) {
            const match = String(tag || '').match(/^v?(\\d+)\\.(\\d+)/);
            return match ? match[1] + '.' + match[2] : String(tag || '');
        }

        // Tag prarilis/beta: "1.1-dev.8", "2.0-beta.1", "1.2-rc.1". Rilis stabil ("1.1", "2.0.3") bukan prarilis.
        function isPrereleaseTag(tag) {
            return /[-.](dev|alpha|beta|rc|pre)/i.test(String(tag || ''));
        }

        function getHiddenUpdateSeries() {
            try {
                const list = JSON.parse(safeStorage.getItem('update_hidden_series') || '[]');
                return Array.isArray(list) ? list.map(String) : [];
            } catch (error) { return []; }
        }

        function getSkippedUpdateTag() { return safeStorage.getItem('update_skipped_tag') || ''; }

        // Aturan tampil pada pemeriksaan OTOMATIS (pemeriksaan manual tidak memakai aturan ini).
        function shouldAutoShowUpdate(info) {
            if (!info || !info.tag_name) return false;
            if (info.tag_name === getSkippedUpdateTag()) return false;
            // "Jangan tampilkan lagi" hanya menyembunyikan update BETA dari seri itu; rilis stabil tetap muncul.
            if (isPrereleaseTag(info.tag_name) && getHiddenUpdateSeries().includes(updateSeries(info.tag_name))) return false;
            return true;
        }

        function setUpdateModalState(state, title, subtitle, icon) {
            UM_STATES.forEach(name => {
                const el = document.getElementById('um-' + name);
                if (el) el.classList.toggle('hidden', name !== state);
            });
            const titleEl = document.getElementById('um-title');
            if (titleEl && title) titleEl.innerText = title;
            const subEl = document.getElementById('um-subtitle');
            if (subEl) subEl.innerText = subtitle || '';
            const iconEl = document.getElementById('um-icon');
            if (iconEl && icon) iconEl.innerText = icon;
        }

        function openUpdateModal() { openModal('updateModal', 'updateBox'); }

        function closeUpdateModal() {
            if (umDownloading) return;   // unduhan berjalan: modal tidak boleh ditutup
            closeModal('updateModal', 'updateBox');
        }

        function showUpdateAvailable(info) {
            umInfo = info;
            document.getElementById('um-current').innerText = info.current_version || '-';
            document.getElementById('um-latest').innerText = info.name || info.tag_name;
            document.getElementById('um-size').innerText = info.asset_size > 0 ? formatBytes(info.asset_size) : '—';
            document.getElementById('um-channel').innerText = info.channel === 'beta' ? 'Beta' : 'Stable';
            // "Jangan tampilkan lagi" hanya tersedia untuk update beta; rilis stabil selalu diberitahukan.
            const canHide = isPrereleaseTag(info.tag_name);
            const hideButton = document.getElementById('um-btn-hide');
            const skipButton = document.getElementById('um-btn-skip');
            const hint = document.getElementById('um-hide-hint');
            if (hideButton) hideButton.classList.toggle('hidden', !canHide);
            if (skipButton) skipButton.classList.toggle('col-span-2', !canHide);
            if (hint) {
                hint.classList.toggle('hidden', !canHide);
                hint.innerText = canHide
                    ? '“Jangan tampilkan lagi” menyembunyikan update beta seri ' + updateSeries(info.tag_name) +
                      ' berikutnya. Rilis stabil tetap diberitahukan, dan Anda bisa memeriksa manual lewat Pengaturan.'
                    : '';
            }
            const notes = document.getElementById('um-notes');
            if (notes) { try { renderReleaseNotes('um-notes', info); } catch (error) { notes.classList.add('hidden'); } }
            const when = formatReleaseDate(info.published_at);
            setUpdateModalState('available', 'Update tersedia', when ? 'Dirilis ' + when : 'Versi baru siap diunduh', '🚀');
        }

        function showUpdateNone(result) {
            const channel = result && result.channel === 'beta' ? 'Beta' : 'Stable';
            const current = (result && result.current_version) || '';
            const text = (result && result.message) || 'Aplikasi sudah menggunakan versi terbaru.';
            document.getElementById('um-none-text').innerText =
                'Tidak ada update. ' + text + (current ? ' Versi terpasang: ' + current + '.' : '');
            setUpdateModalState('none', 'Tidak ada update', 'Kanal ' + (currentUpdateChannel() === 'beta' ? 'Beta' : channel), '✅');
        }

        function showUpdateError(message, action) {
            umRetryAction = action || 'check';
            document.getElementById('um-error-text').innerText = message;
            setUpdateModalState('error', 'Pembaruan gagal', '', '⚠️');
            openUpdateModal();
        }

        function retryUpdateAction() {
            if (umRetryAction === 'download' && umInfo) startUpdateDownload();
            else runUpdateCheck(true);
        }

        async function runUpdateCheck(manual) {
            if (umChecking || umDownloading) return;
            umChecking = true;
            platformSetCheckBusy(true);
            const channel = currentUpdateChannel();
            if (manual) {
                setUpdateModalState('checking', 'Memeriksa update', 'Kanal ' + (channel === 'beta' ? 'Beta' : 'Stable'), '🔎');
                openUpdateModal();
            } else {
                platformSetUpdateStatus('Memeriksa update di GitHub…');
            }
            let result;
            try {
                result = await platformCheckUpdate(channel);
            } catch (error) {
                result = { update_available: false, error: 'Gagal memeriksa update: ' + ((error && error.message) || error) };
            } finally {
                umChecking = false;
                platformSetCheckBusy(false);
            }
            result = result || { update_available: false, error: 'Tidak ada respons dari pemeriksa update.' };
            platformRenderNotes(result);

            if (result.error) {
                platformSetUpdateStatus(result.error, true);
                platformSetUpdateDetails(result.error);
                if (manual) showUpdateError(result.error, 'check');
                return;
            }
            umInfo = result;
            if (result.update_available) {
                const label = (result.name || result.tag_name) + ' (' + (result.channel === 'beta' ? 'Beta' : 'Stable') + ')';
                platformSetUpdateStatus('Update tersedia: ' + label + '.');
                platformSetUpdateDetails('Tersedia ' + label + '. ' + (result.published_at ? 'Dirilis ' + formatReleaseDate(result.published_at) : ''));
                if (manual) { showUpdateAvailable(result); return; }
                if (!shouldAutoShowUpdate(result)) {
                    platformSetUpdateStatus('Update ' + label + ' tersedia, tetapi disembunyikan. Tekan Periksa Update untuk melihatnya.');
                    return;
                }
                if (umAutoShownTag === result.tag_name) return;   // sudah ditampilkan pada sesi ini
                umAutoShownTag = result.tag_name;
                showUpdateAvailable(result);
                openUpdateModal();
            } else {
                const message = result.message || 'Aplikasi sudah menggunakan versi terbaru untuk kanal ini.';
                platformSetUpdateStatus(message);
                platformSetUpdateDetails(message);
                if (manual) showUpdateNone(result);
            }
        }

        function skipUpdateVersion() {
            if (!umInfo) return;
            safeStorage.setItem('update_skipped_tag', umInfo.tag_name);
            const message = 'Versi ' + umInfo.tag_name + ' dilewati. Update berikutnya tetap akan diberitahukan.';
            closeUpdateModal();
            platformSetUpdateStatus(message);
            if (typeof showConnectionNotice === 'function') showConnectionNotice('info', '⏭ ' + message, 6000);
        }

        function hideUpdateSeries() {
            if (!umInfo || !isPrereleaseTag(umInfo.tag_name)) return;   // rilis stabil tidak bisa disembunyikan
            const series = updateSeries(umInfo.tag_name);
            const list = getHiddenUpdateSeries();
            if (!list.includes(series)) list.push(series);
            safeStorage.setItem('update_hidden_series', JSON.stringify(list));
            const message = 'Update beta seri ' + series + ' disembunyikan. Rilis stabil tetap diberitahukan; periksa manual di Pengaturan untuk melihat beta lagi.';
            closeUpdateModal();
            platformSetUpdateStatus(message);
            if (typeof showConnectionNotice === 'function') showConnectionNotice('info', '🚫 ' + message, 7000);
        }

        function resetUpdatePreferences() {
            safeStorage.removeItem('update_skipped_tag');
            safeStorage.removeItem('update_hidden_series');
            umAutoShownTag = null;
            platformSetUpdateStatus('Pilihan lewati/sembunyikan update telah direset.');
        }

        function applyUpdateProgress(p) {
            const downloaded = Number(p.downloaded) || 0;
            const total = Number(p.total) > 0 ? Number(p.total) : ((umInfo && umInfo.asset_size) || 0);
            const percent = total > 0 ? Math.min(100, Math.max(0, downloaded * 100 / total)) : Math.min(100, Math.max(0, Number(p.percent) || 0));
            document.getElementById('um-dl-status').innerText = p.status || 'Mengunduh update…';
            document.getElementById('um-dl-percent').innerText = total > 0 || p.percent > 0 ? Math.floor(percent) + '%' : formatBytes(downloaded);
            document.getElementById('um-dl-bar').style.width = percent + '%';
            document.getElementById('um-dl-size').innerText = formatBytes(downloaded) + ' / ' + (total > 0 ? formatBytes(total) : '?');
            document.getElementById('um-dl-speed').innerText = formatBytes(Number(p.speed_bps) || 0) + '/dtk';
            document.getElementById('um-dl-eta').innerText = total > 0 && p.eta_seconds !== null && p.eta_seconds !== undefined ? formatEta(Number(p.eta_seconds)) : 'menghitung…';
        }

        async function startUpdateDownload() {
            if (!umInfo || umDownloading) return;
            umDownloading = true;
            const info = umInfo;
            document.getElementById('um-dl-version').innerText = info.name || info.tag_name;
            document.getElementById('um-dl-close').classList.add('hidden');
            document.getElementById('um-dl-note').innerText = 'Jangan tutup aplikasi selama unduhan berlangsung.';
            setUpdateModalState('downloading', 'Mengunduh update', info.name || info.tag_name, '⬇️');
            applyUpdateProgress({ downloaded: 0, total: info.asset_size || 0, percent: 0, speed_bps: 0, eta_seconds: null, status: 'Menghubungkan ke server…' });
            try {
                const message = await platformDownloadUpdate(info, currentUpdateChannel(), applyUpdateProgress);
                applyUpdateProgress({ downloaded: info.asset_size || 1, total: info.asset_size || 1, percent: 100, speed_bps: 0, eta_seconds: 0, status: message || 'Unduhan selesai.' });
                document.getElementById('um-dl-note').innerText = message || 'Unduhan selesai.';
                umDownloading = false;
                document.getElementById('um-dl-close').classList.remove('hidden');
            } catch (error) {
                umDownloading = false;
                showUpdateError(((error && error.message) || String(error)), 'download');
            }
        }

        function scheduleAutoUpdateChecks() {
            // Hanya memeriksa (dan menampilkan modal bila ada update); tidak pernah mengunduh otomatis.
            whenSplashDone(() => {
                setTimeout(() => { if (autoUpdateEnabled()) runUpdateCheck(false); }, 1800);
                setInterval(() => { if (autoUpdateEnabled()) runUpdateCheck(false); }, 6 * 60 * 60 * 1000);
            });
        }

        // ----- Adaptor desktop (pywebview) untuk modal update -----
        function currentUpdateChannel() {
            const select = document.getElementById('setting-update-channel');
            return select && select.value === 'beta' ? 'beta' : 'stable';
        }

        function autoUpdateEnabled() {
            const box = document.getElementById('setting-auto-update-check');
            return !!(box && box.checked);
        }

        function setUpdateStatus(message, isError = false) {
            const el = document.getElementById('update-status');
            if (!el) return;
            el.innerText = message;
            el.className = 'text-[10px] ' + (isError ? 'text-orange-300' : 'text-slate-400');
        }

        function platformSetUpdateStatus(message, isError) { setUpdateStatus(message, !!isError); }

        function platformSetUpdateDetails(message) {
            const el = document.getElementById('about-update-details');
            if (el) el.innerText = message;
        }

        function platformRenderNotes(result) {
            renderReleaseNotes('release-notes', result && !result.error ? result : null);
        }

        function platformSetCheckBusy(busy) {
            const btn = document.getElementById('btn-check-update');
            if (btn) { btn.disabled = !!busy; btn.innerText = busy ? 'Memeriksa…' : '🔎 Periksa Update'; }
        }

        async function platformCheckUpdate(channel) {
            if (!window.pywebview || !window.pywebview.api || typeof window.pywebview.api.check_for_updates !== 'function') {
                return { update_available: false, error: 'API updater belum siap. Coba lagi beberapa detik lagi.' };
            }
            return await window.pywebview.api.check_for_updates(channel);
        }

        async function platformDownloadUpdate(info, channel, onProgress) {
            if (!window.pywebview || !window.pywebview.api || typeof window.pywebview.api.install_update !== 'function') {
                throw new Error('API updater belum siap. Coba lagi beberapa detik lagi.');
            }
            const timer = setInterval(async () => {
                try { onProgress(await window.pywebview.api.get_update_progress()); } catch (error) { /* abaikan */ }
            }, 500);
            try {
                const result = await window.pywebview.api.install_update(info.tag_name, channel);
                if (!result || !result.success) throw new Error((result && result.error) || 'Pemasangan update gagal.');
                return 'Update terpasang. Aplikasi akan dimulai ulang…';
            } finally {
                clearInterval(timer);
            }
        }

        // ----- Jalankan saat Windows dimulai (hanya EXE hasil instalasi) -----
        async function loadStartupSetting() {
            try {
                if (!window.pywebview || !window.pywebview.api || typeof window.pywebview.api.get_startup_status !== 'function') return;
                const status = await window.pywebview.api.get_startup_status();
                const row = document.getElementById('startup-setting');
                if (!row || !status || !status.supported) return;
                document.getElementById('setting-startup').checked = !!status.enabled;
                row.classList.remove('hidden');
                if (typeof resizeSettingsContent === 'function') resizeSettingsContent(activeSettingsTab, false);
            } catch (error) {
                console.error('Gagal membaca pengaturan startup:', error);
            }
        }

        async function changeStartup(enabled) {
            const box = document.getElementById('setting-startup');
            const note = document.getElementById('startup-status');
            try {
                const result = await window.pywebview.api.set_startup(!!enabled);
                if (!result || !result.success) throw new Error((result && result.error) || 'Gagal mengubah pengaturan.');
                note.innerText = enabled ? 'Aplikasi akan berjalan otomatis saat Windows dimulai.' : 'Aplikasi tidak lagi berjalan otomatis saat Windows dimulai.';
                note.className = 'text-[10px] text-emerald-400 mt-1';
            } catch (error) {
                box.checked = !enabled;
                note.innerText = 'Gagal: ' + ((error && error.message) || error);
                note.className = 'text-[10px] text-orange-400 mt-1';
            }
        }


        function saveUpdatePreferences() {
            safeStorage.setItem('update_channel', document.getElementById('setting-update-channel').value);
            safeStorage.setItem('auto_update_check', String(document.getElementById('setting-auto-update-check').checked));
        }













        function openExternalUrl(url) {
            if (window.pywebview && window.pywebview.api && typeof window.pywebview.api.open_url === 'function') {
                window.pywebview.api.open_url(url);
            } else {
                window.open(url, '_blank');
            }
        }

        function savePopupPreferences() {
            safeStorage.setItem('suppress_tower_popup', String(document.getElementById('suppress-tower-popup').checked));
            safeStorage.setItem('suppress_internet_popup', String(document.getElementById('suppress-internet-popup').checked));
        }

        function resetPopupPreferences() {
            safeStorage.removeItem('suppress_tower_popup');
            safeStorage.removeItem('suppress_internet_popup');
            document.getElementById('suppress-tower-popup').checked = false;
            document.getElementById('suppress-internet-popup').checked = false;
        }

        function shouldShowIssuePopup(kind) {
            // Default: SELALU tampil. Disembunyikan hanya jika pengguna mencentang
            // "Jangan tampilkan pop-up ini lagi" (atau opsi yang sama di Pengaturan).
            const key = kind === 'tower' ? 'suppress_tower_popup' : 'suppress_internet_popup';
            return safeStorage.getItem(key) !== 'true';
        }

        let activeIssuePopupKind = null;

        // ===== Deskripsi gangguan & perkiraan penyebab =====
        // Aplikasi tidak bisa mengetahui penyebab pastinya. Perkiraan dibuat dari pola
        // sinyal sebelum gangguan (melemah bertahap vs putus mendadak) dan dari ping
        // ke Cloudflare, lalu ditampilkan sebagai "kemungkinan", bukan diagnosis.
        const TOWER_CAUSES = {
            weather: { icon: '🌧️', title: 'Cuaca ekstrem', desc: 'Hujan lebat, badai, atau petir meredam sinyal dan bisa mengganggu perangkat tower.' },
            overheat: { icon: '🌡️', title: 'Pemancar overheat', desc: 'Perangkat pemancar (BTS) terlalu panas, misalnya pendingin gagal, lalu menurunkan daya atau mati sementara.' },
            power: { icon: '⚡', title: 'Listrik atau baterai tower bermasalah', desc: 'Pemadaman listrik di lokasi tower dan baterai cadangan sudah habis.' },
            backhaul: { icon: '🔌', title: 'Kabel backhaul putus', desc: 'Jalur kabel atau fiber dari tower ke jaringan operator terputus, misalnya karena galian, pohon tumbang, atau kabel rusak.' },
            maintenance: { icon: '🛠️', title: 'Pemeliharaan atau upgrade tower', desc: 'Operator sedang maintenance atau upgrade jaringan. Biasanya sementara dan sering dilakukan dini hari.' },
            congestion: { icon: '👥', title: 'Tower terlalu padat', desc: 'Terlalu banyak pengguna di satu sel sehingga router sulit mempertahankan koneksi.' },
            handover: { icon: '🔁', title: 'Perpindahan atau perubahan sel', desc: 'Router berpindah ke sel lain atau operator mengubah konfigurasi sel sehingga koneksi sempat hilang.' },
            local: { icon: '📡', title: 'Masalah di sisi router atau antena', desc: 'Posisi router kurang baik, kabel atau konektor antena longgar, atau router perlu di-restart.' }
        };
        const INTERNET_CAUSES = {
            testserver: { icon: '🧪', title: 'Server uji tidak terjangkau (alarm palsu)', desc: 'Aplikasi menguji lewat 1.1.1.1. Jika situs lain masih bisa dibuka, internet sebenarnya normal.' },
            quota: { icon: '📶', title: 'Indikasi Diblokir', desc: 'Router masih tersambung ke tower, tetapi operator memblokir data. Silahkan kontak CS' },
            dns: { icon: '🌐', title: 'Gangguan DNS operator', desc: 'Nama situs gagal diterjemahkan ke alamat sehingga internet terasa mati padahal sinyal ada.' },
            upstream: { icon: '🔌', title: 'Jalur internet operator terganggu', desc: 'Gangguan di backbone atau gateway operator di luar tower, misalnya kabel atau perangkat jaringan inti.' },
            apn: { icon: '⚙️', title: 'Pengaturan APN atau profil data bermasalah', desc: 'Biasanya muncul setelah pengaturan router diubah atau di-reset.' },
            congestion: { icon: '👥', title: 'Jaringan padat atau sinyal lemah', desc: 'Banyak paket data hilang sehingga tes gagal meskipun tower tersambung.' }
        };
        const ISSUE_TIPS = {
            tower: [
                'Tunggu 3-5 menit; banyak gangguan tower pulih sendiri.',
                'Cek apakah HP lain di lokasi yang sama juga kehilangan sinyal.',
                'Restart router: cabut listrik 30 detik lalu nyalakan lagi.',
                'Pindahkan router atau antena ke dekat jendela atau tempat yang lebih tinggi.',
                'Jika lebih dari 30 menit, hubungi CS dan tanyakan gangguan di area Anda.'
            ],
            internet: [
                'Cek sisa masa aktif paket IRA.',
                'Coba buka situs lain; jika bisa, kemungkinan hanya server uji yang bermasalah.',
                'Restart router: cabut listrik 30 detik lalu nyalakan lagi.',
                'Coba ganti DNS perangkat ke 8.8.8.8 atau 9.9.9.9.',
                'Jika berlangsung lama, hubungi CS.'
            ]
        };
        const signalHistory = [];
        let lastPingOkAt = 0;
        const issueStartedAt = { tower: null, internet: null };
        const issueDiagnosis = { tower: null, internet: null };

        function recordSignalSample(data) {
            const rsrp = parseFloat(data.nr5g_rsrp);
            if (!Number.isFinite(rsrp) || rsrp === 0) return;
            const sinr = parseFloat(data.nr5g_snr);
            const rsrq = parseFloat(data.nr5g_rsrq);
            signalHistory.push({
                rsrp: rsrp,
                sinr: Number.isFinite(sinr) ? sinr : null,
                rsrq: Number.isFinite(rsrq) ? rsrq : null,
                pci: data.nr5g_pci || null
            });
            if (signalHistory.length > 15) signalHistory.shift();
        }

        function rankCauses(causeMap, score, summary, note) {
            const keys = Object.keys(score).filter(k => score[k] > 0).sort((a, b) => score[b] - score[a]).slice(0, 5);
            const causes = keys.map((k, i) => Object.assign({ key: k, likely: i < 2 && score[k] >= 3 }, causeMap[k]));
            return { summary: summary, note: note, causes: causes };
        }

        function diagnoseTower() {
            const n = signalHistory.length;
            const last = n ? signalHistory[n - 1] : null;
            const first = n ? signalHistory[0] : null;
            const score = { weather: 1, overheat: 0, power: 0, backhaul: 1, maintenance: 0, congestion: 0, handover: 0, local: 1 };
            let summary, note = '';
            if (!last) {
                summary = 'Tidak ada data sinyal sebelum terputus, jadi penyebab tidak bisa diperkirakan. Berikut kemungkinan yang umum terjadi.';
            } else {
                const weak = last.rsrp <= -105 || (last.sinr !== null && last.sinr <= 3) || (last.rsrq !== null && last.rsrq <= -16);
                const falling = n >= 4 && (first.rsrp - last.rsrp) >= 8;
                const detail = 'RSRP ' + last.rsrp + ' dBm' + (last.sinr !== null ? ', SINR ' + last.sinr + ' dB' : '');
                if (weak || falling) {
                    score.weather += 3;
                    score.local += last.rsrp <= -115 ? 2 : 1;
                    if (last.sinr !== null && last.sinr <= 5) score.congestion += 2;
                    summary = 'Sinyal sudah melemah sebelum terputus (' + detail + '). Pola ini lebih sering terjadi karena cuaca, halangan, atau tower padat.';
                    note = 'Perkiraan: sinyal melemah sebelum putus (cuaca, halangan, atau tower padat).';
                } else {
                    score.backhaul += 3;
                    score.power += 2;
                    score.overheat += 2;
                    score.maintenance += 1;
                    summary = 'Sinyal masih kuat sebelum terputus (' + detail + '). Putus mendadak seperti ini biasanya masalah di sisi tower atau operator.';
                    note = 'Perkiraan: putus mendadak saat sinyal kuat (sisi tower atau operator).';
                }
                const pcis = new Set(signalHistory.map(x => x.pci).filter(Boolean));
                if (pcis.size > 1) score.handover += 2;
            }
            const hour = new Date().getHours();
            if (hour < 5) score.maintenance += 2;
            if (hour >= 11 && hour < 16) score.overheat += 1;
            return rankCauses(TOWER_CAUSES, score, summary, note);
        }

        function diagnoseInternet() {
            const score = { quota: 2, dns: 2, upstream: 2, apn: 1, congestion: 0, testserver: 0 };
            const last = signalHistory.length ? signalHistory[signalHistory.length - 1] : null;
            let summary, note;
            if (Date.now() - lastPingOkAt < 10000) {
                score.testserver += 5;
                summary = 'Tes ke 1.1.1.1 gagal, tetapi ping ke Cloudflare masih berhasil. Kemungkinan ini alarm palsu karena 1.1.1.1 terblokir, bukan internet mati.';
                note = 'Perkiraan: ping Cloudflare masih berhasil (kemungkinan alarm palsu).';
            } else {
                score.upstream += 1;
                summary = 'Tower tersambung, tetapi data internet tidak mengalir.';
                note = 'Perkiraan: data tidak mengalir meski tower tersambung.';
            }
            if (last && (last.rsrp <= -105 || (last.sinr !== null && last.sinr <= 5))) {
                score.congestion += 3;
                summary += ' Kualitas sinyal sedang lemah sehingga banyak paket gagal.';
            }
            return rankCauses(INTERNET_CAUSES, score, summary, note);
        }

        function getIssueDiagnosis(kind) {
            if (!issueDiagnosis[kind]) issueDiagnosis[kind] = kind === 'tower' ? diagnoseTower() : diagnoseInternet();
            return issueDiagnosis[kind];
        }

        function issueNote(kind) {
            issueDiagnosis[kind] = null;
            return getIssueDiagnosis(kind).note;
        }

        function renderIssueDetails(kind) {
            const box = document.getElementById('disc-details');
            if (!box) return;
            const diag = getIssueDiagnosis(kind);
            const parts = [];
            parts.push('<div class="text-[11px] text-slate-300 bg-slate-950/60 border border-slate-800 rounded-lg p-2 mb-2">' + diag.summary + '</div>');
            parts.push('<div class="text-[10px] font-bold text-orange-300 uppercase tracking-wider mb-1">Kemungkinan penyebab</div>');
            diag.causes.forEach(c => {
                parts.push('<div class="flex gap-2 py-1.5 border-b border-slate-800/60 last:border-0">'
                    + '<div class="text-base leading-none">' + c.icon + '</div>'
                    + '<div class="min-w-0"><div class="text-[11px] font-semibold text-slate-100">' + c.title
                    + (c.likely ? ' <span class="ml-1 text-[9px] font-bold text-orange-300 bg-orange-500/15 border border-orange-500/40 rounded px-1">Paling mungkin</span>' : '')
                    + '</div><div class="text-[10px] text-slate-400">' + c.desc + '</div></div></div>');
            });
            parts.push('<div class="text-[10px] font-bold text-cyan-300 uppercase tracking-wider mt-2 mb-1">Yang bisa dicoba</div>');
            parts.push('<ul class="text-[10px] text-slate-300 list-disc pl-4 space-y-0.5">' + ISSUE_TIPS[kind].map(t => '<li>' + t + '</li>').join('') + '</ul>');
            parts.push('<p class="text-[9px] text-slate-500 mt-2">Perkiraan otomatis dari pola sinyal sebelum gangguan, bukan diagnosis pasti. Hanya operator yang bisa memastikan penyebabnya.</p>');
            box.innerHTML = parts.join('');
            box.scrollTop = 0;
        }

        function refreshIssueElapsed() {
            const kind = activeIssuePopupKind;
            const el = document.getElementById('disc-elapsed');
            if (!kind || !el || !issueStartedAt[kind]) return;
            const sec = Math.max(0, Math.floor((Date.now() - issueStartedAt[kind]) / 1000));
            const mm = Math.floor(sec / 60);
            el.innerText = 'Berlangsung: ' + (mm > 0 ? mm + ' mnt ' : '') + (sec % 60) + ' dtk'
                + (sec >= 600 ? ' - sudah cukup lama, sebaiknya hubungi operator.' : '');
        }

        function showIssuePopup(kind) {
            activeIssuePopupKind = kind;
            const isTower = kind === 'tower';
            document.getElementById('modal-title-disc').innerText = isTower ? 'KONEKSI TOWER TERPUTUS!' : 'INTERNET BERMASALAH!';
            document.getElementById('modal-desc-disc').innerText = isTower
                ? 'Sinyal tower tidak terdeteksi atau terputus dari jaringan utama.'
                : 'Tower tersambung, tetapi akses internet gagal.';
            const checkbox = document.getElementById('disc-suppress-checkbox');
            if (checkbox) checkbox.checked = false;
            renderIssueDetails(kind);
            refreshIssueElapsed();
            openModal('disconnectModal', 'disconnectBox');
        }

        function onIssuePopupSuppressChange(checked) {
            if (!activeIssuePopupKind) return;
            const isTower = activeIssuePopupKind === 'tower';
            safeStorage.setItem(isTower ? 'suppress_tower_popup' : 'suppress_internet_popup', String(checked));
            // Sinkronkan dengan checkbox di Pengaturan.
            const settingCheckbox = document.getElementById(isTower ? 'suppress-tower-popup' : 'suppress-internet-popup');
            if (settingCheckbox) settingCheckbox.checked = checked;
        }

        function closeIssuePopup(kind) {
            // Dipanggil saat koneksi pulih: tutup pop-up dan reset data diagnosis.
            if (activeIssuePopupKind === kind) closeDisconnectModal();
            issueStartedAt[kind] = null;
            issueDiagnosis[kind] = null;
            if (kind === 'tower') signalHistory.length = 0;
        }

        // Alur gangguan disamakan dengan alur "kembali normal": banner SELALU tampil
        // (tidak bergantung preferensi), ditambah pop-up kecuali disembunyikan pengguna.
        function notifyIssue(kind, message) {
            issueStartedAt[kind] = Date.now();
            showConnectionNotice('issue', message);
            if (shouldShowIssuePopup(kind)) showIssuePopup(kind);
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

        // ===== Pergantian tema dengan animasi halus =====
        // Utama: View Transitions API (lingkaran yang meluas dari pemilih tema, dianimasikan
        // di GPU). Cadangan: transisi warna CSS. Dilewati jika pengguna memilih mengurangi gerakan.
        let themeTransitionTimer = null;

        function applyThemeClasses(theme) {
            const body = document.getElementById('app-body');
            if (theme === 'light') {
                body.className = body.className.replace('bg-slate-950 text-slate-100', 'bg-slate-100 text-slate-900');
            } else {
                body.className = body.className.replace('bg-slate-100 text-slate-900', 'bg-slate-950 text-slate-100');
            }
            body.classList.toggle('theme-light', theme === 'light');
        }

        function changeTheme(theme, save = true) {
            if (save) {
                safeStorage.setItem('router_theme', theme);
            }
            const root = document.documentElement;
            const body = document.getElementById('app-body');
            const reduceMotion = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
            const unchanged = body.classList.contains('theme-light') === (theme === 'light');
            // Tanpa animasi saat memuat pengaturan, tema sama, atau gerakan dikurangi.
            if (!save || unchanged || reduceMotion) {
                applyThemeClasses(theme);
                return;
            }

            if (typeof document.startViewTransition === 'function') {
                const select = document.getElementById('setting-theme');
                const rect = select ? select.getBoundingClientRect() : null;
                const hasRect = !!rect && Number.isFinite(rect.left) && Number.isFinite(rect.top);
                const x = hasRect ? rect.left + (rect.width || 0) / 2 : window.innerWidth / 2;
                const y = hasRect ? rect.top + (rect.height || 0) / 2 : window.innerHeight / 2;
                const radius = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y));
                const cleanup = () => root.classList.remove('theme-vt');
                root.classList.add('theme-vt');
                try {
                    const transition = document.startViewTransition(() => applyThemeClasses(theme));
                    transition.ready.then(() => {
                        root.animate(
                            { clipPath: ['circle(0px at ' + x + 'px ' + y + 'px)', 'circle(' + radius + 'px at ' + x + 'px ' + y + 'px)'] },
                            { duration: 800, easing: 'cubic-bezier(0.4, 0, 0.2, 1)', pseudoElement: '::view-transition-new(root)' }
                        );
                    }).catch(() => {});
                    transition.finished.then(cleanup, cleanup);
                } catch (error) {
                    cleanup();
                    applyThemeClasses(theme);
                }
                return;
            }

            // Cadangan: transisi warna CSS untuk seluruh elemen selama pergantian.
            root.classList.add('theme-animating');
            void root.offsetWidth;
            applyThemeClasses(theme);
            clearTimeout(themeTransitionTimer);
            themeTransitionTimer = setTimeout(() => root.classList.remove('theme-animating'), 900);
        }

        function changeFrequency(val) {
            currentIntervalTime = parseInt(val, 10) || 1000;
            safeStorage.setItem('router_freq', String(currentIntervalTime));
            if (window.pywebview && window.pywebview.api) startPolling();
            updatePingMonitorFrequency();
        }

        function addHistoryLog(status, timeStr, note = '') {
            const isConn = status.includes('Tersambung') || status.includes('Normal');
            const logItem = { status: status, time: timeStr, type: isConn ? 'connect' : 'disconnect', note: note || '' };
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
                                ${item.note ? '<div class="text-[10px] text-slate-500 mt-0.5">' + item.note + '</div>' : ''}
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
        function safeApplyDynamicYAxis(chart) {
            try { applyDynamicYAxis(chart); }
            catch (error) { console.error("Gagal mengatur skala grafik:", error); }
        }

        function applyDynamicYAxis(chart) {
            const values = chart.data.datasets.flatMap(dataset => dataset.data)
                .map(Number).filter(value => Number.isFinite(value));
            if (!values.length) return;
            const minValue = Math.min(...values);
            const maxValue = Math.max(...values);
            const span = maxValue - minValue;
            // Center the newest sample vertically: use a symmetric Y range around
            // the latest reading while retaining a sensible scale for the history.
            const latestValue = Number(chart.data.datasets[0].data.slice(-1)[0]);
            if (Number.isFinite(latestValue)) {
                const deviation = Math.max(
                    Math.abs(latestValue - minValue),
                    Math.abs(maxValue - latestValue)
                );
                const centeredSpan = Math.max(deviation * 1.25, 1);
                let centeredStep;
                if (centeredSpan <= 2) centeredStep = 1;
                else {
                    const rawStep = (centeredSpan * 2) / 4;
                    const magnitude = Math.pow(10, Math.floor(Math.log10(rawStep)));
                    const normalized = rawStep / magnitude;
                    centeredStep = (normalized <= 1 ? 1 : normalized <= 2 ? 2 : normalized <= 5 ? 5 : 10) * magnitude;
                }
                const halfRange = Math.max(centeredStep * 2, Math.ceil(centeredSpan / centeredStep) * centeredStep);
                chart.options.scales.y.min = Number((latestValue - halfRange).toFixed(6));
                chart.options.scales.y.max = Number((latestValue + halfRange).toFixed(6));
                chart.options.scales.y.ticks.stepSize = centeredStep;
                return;
            }
            let step;
            if (span <= 3) {
                step = 1;
            } else {
                const rawStep = span / 3;
                const magnitude = Math.pow(10, Math.floor(Math.log10(rawStep)));
                const normalized = rawStep / magnitude;
                step = (normalized <= 1 ? 1 : normalized <= 2 ? 2 : normalized <= 5 ? 5 : 10) * magnitude;
            }
            if (!Number.isFinite(step) || step <= 0) step = 1;
            let axisMin = Math.floor(minValue / step) * step;
            let axisMax = Math.ceil(maxValue / step) * step;
            if (axisMin === axisMax) axisMin -= step;
            // Add one tick above the strongest reading so labels remain readable
            // when values fall between integer ticks (e.g. -21.5).
            axisMax += step;
            chart.options.scales.y.min = Number(axisMin.toFixed(6));
            chart.options.scales.y.max = Number(axisMax.toFixed(6));
            chart.options.scales.y.ticks.stepSize = step;
        }

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
                            ticks: { font: { size: 9 }, color: '#94a3b8', maxTicksLimit: 5, stepSize: 1 }
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
        let pingMonitorInterval = Number.parseInt(safeStorage.getItem('router_ping_freq') || '2000', 10);
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
                        lastPingOkAt = Date.now();
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
                        applyDynamicYAxis(chartPing);
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
                    document.getElementById('text-ping').className = 'font-semibold text-orange-400';
                    document.getElementById('dot-ping').className = 'h-1.5 w-1.5 rounded-full bg-orange-400';
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
                safeStorage.setItem('router_ping_freq', String(interval));
                const title = document.getElementById('ping-chart-title');
                if (title) title.textContent = '📈 Ping Latency — setiap ' + (interval / 1000) + ' detik';
                if (window.pywebview && window.pywebview.api) startPingMonitor();
                return;
            }
            customInput.classList.add('hidden');
            if (val === 'auto') {
                safeStorage.setItem('router_ping_freq', 'auto');
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

        // ===== NR-ARFCN -> frekuensi (3GPP TS 38.104, tabel 5.4.2.1-1) =====
        // Contoh: NR-ARFCN 288270 = 288270 x 5 kHz = 1441,35 MHz = 1,441 GHz.
        function nrArfcnToMHz(arfcn) {
            const n = Number(arfcn);
            if (!Number.isInteger(n) || n < 0 || n > 3279165) return null;
            if (n < 600000) return n * 0.005;                          // 0 - 3000 MHz, langkah 5 kHz
            if (n < 2016667) return 3000 + (n - 600000) * 0.015;       // 3000 - 24250 MHz, langkah 15 kHz
            return 24250.08 + (n - 2016667) * 0.06;                    // 24250 - 100000 MHz, langkah 60 kHz
        }

        function describeNrArfcn(raw) {
            const text = String(raw === undefined || raw === null ? '' : raw).trim();
            if (!/^\\d+$/.test(text)) return { channel: '-', freq: '-' };
            const mhz = nrArfcnToMHz(Number(text));
            if (mhz === null) return { channel: text, freq: 'di luar rentang NR-ARFCN' };
            return { channel: text, freq: mhz.toFixed(2) + ' MHz / ' + (mhz / 1000).toFixed(3) + ' GHz' };
        }

        function updateArfcnInfo(raw) {
            const info = describeNrArfcn(raw);
            const channelEl = document.getElementById('info-arfcn');
            const freqEl = document.getElementById('info-arfcn-freq');
            if (channelEl) channelEl.innerText = info.channel;
            if (freqEl) freqEl.innerText = info.freq;
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
            if (rawTowerConnected) recordSignalSample(data);

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
                    notifyIssue('tower', '⚠️ GANGGUAN TOWER: sinyal tower tidak terdeteksi.');
                } else if (!wasInternetOk) {
                    internetIssueNotified = true;
                    notifyIssue('internet', '🌐 GANGGUAN INTERNET: tower tersambung, akses internet gagal.');
                }
            } else {
                // Require repeated readings before changing state; this prevents transient request
                // failures from alternating between "gangguan" and "kembali normal".
                if (rawTowerConnected) {
                    towerSuccessCount++;
                    towerFailCount = 0;
                    if (!wasConnected && towerSuccessCount >= 3) {
                        wasConnected = true;
                        closeIssuePopup('tower');
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
                        addHistoryLog('Tower Terputus', nowTime, issueNote('tower'));
                        playAlertSound();
                        towerIssueNotified = true;
                        notifyIssue('tower', '⚠️ GANGGUAN TOWER: koneksi tower terputus.');
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
                        closeIssuePopup('internet');
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
                        addHistoryLog('Internet Bermasalah', nowTime, issueNote('internet'));
                        playAlertSound();
                        notifyIssue('internet', '🌐 GANGGUAN INTERNET: tower aktif, tetapi akses internet gagal.');
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
                applyDynamicYAxis(chart);
                // Keep a short smooth transition; the fixed-size history prevents runaway points.
                chart.update();
            }

            updateChartData(chartRsrp, rsrp);
            updateChartData(chartRssi, rssi);
            updateChartData(chartRsrq, rsrq);
            updateChartData(chartSinr, sinr);

            // Static info without animations
            document.getElementById('info-pci').innerText = data.nr5g_pci || '-';
            updateArfcnInfo(data.nr5g_action_channel);
            document.getElementById('info-cellid').innerText = data.nr5g_cell_id || '-';
            document.getElementById('info-nettype').innerText = data.network_type || '-';
            document.getElementById('info-signalbar').innerText = (data.signalbar || '0') + ' / 3';
            document.getElementById('info-band').innerText = data.wan_active_band || '-';

            let connEl = document.getElementById('status-conn');
            refreshIssueElapsed();
            connEl.innerText = `Terakhir: ${nowTime}`;
            connEl.className = "text-[11px] font-medium bg-emerald-950/40 border border-emerald-500/30 text-emerald-400 px-3 py-1 rounded-xl shadow-inner";
        }

        const diagnosticErrors = [];
        window.addEventListener('error', event => {
            diagnosticErrors.push({ time: new Date().toISOString(), type: 'error', message: event.message || 'Unknown JS error', source: event.filename || '', line: event.lineno || 0 });
            if (diagnosticErrors.length > 200) diagnosticErrors.shift();
        });
        window.addEventListener('unhandledrejection', event => {
            diagnosticErrors.push({ time: new Date().toISOString(), type: 'unhandledrejection', message: String(event.reason || 'Unknown rejection') });
            if (diagnosticErrors.length > 200) diagnosticErrors.shift();
        });
        function setExportStatus(message, isError = false) {
            // Banner tertutup oleh jendela Pengaturan, jadi hasil juga ditulis di dekat tombol.
            const el = document.getElementById('export-status');
            if (el) {
                el.innerText = message;
                el.className = 'text-[10px] min-h-[14px] break-all ' + (isError ? 'text-orange-400' : 'text-emerald-400');
            }
        }

        async function exportDiagnosticLogs() {
            const report = {
                app: 'IRA ZTE MC8501 5G Live Signal Charts',
                version: typeof APP_VERSION_JS !== 'undefined' ? APP_VERSION_JS : 'unknown',
                exported_at: new Date().toISOString(),
                platform: navigator.userAgent,
                page_url: location.href,
                status: {
                    connection: document.getElementById('status-conn')?.innerText || 'unknown',
                    tower: document.getElementById('tower-status-val')?.innerText || 'unknown',
                    internet: document.getElementById('internet-status-val')?.innerText || 'unknown'
                },
                telemetry: {
                    signalbar: document.getElementById('info-signalbar')?.innerText || 'unknown',
                    network_type: document.getElementById('info-nettype')?.innerText || 'unknown',
                    pci: document.getElementById('info-pci')?.innerText || 'unknown',
                    cell_id: document.getElementById('info-cellid')?.innerText || 'unknown',
                    nr_arfcn: (document.getElementById('info-arfcn')?.innerText || 'unknown') + ' | ' + (document.getElementById('info-arfcn-freq')?.innerText || 'unknown')
                },
                connection_history: Array.isArray(connectionHistory) ? connectionHistory.slice(0, 300) : [],
                signal_history: signalHistory.slice(-15),
                popup_preferences: {
                    suppress_tower_popup: safeStorage.getItem('suppress_tower_popup') === 'true',
                    suppress_internet_popup: safeStorage.getItem('suppress_internet_popup') === 'true'
                },
                javascript_errors: diagnosticErrors.slice(-200),
                settings: {
                    router_poll_interval_ms: safeStorage.getItem('router_freq') || 'default',
                    ping_interval_ms: safeStorage.getItem('router_ping_freq') || 'auto',
                    theme: safeStorage.getItem('router_theme') || 'default'
                },
                note: 'Diagnostic export excludes passwords, cookies, tokens, and router credentials.'
            };
            const json = JSON.stringify(report, null, 2);
            try {
                if (window.pywebview && window.pywebview.api) {
                    if (typeof window.pywebview.api.export_diagnostic_logs !== 'function') {
                        setExportStatus('Fitur ekspor belum siap. Coba lagi beberapa detik lagi.', true);
                        return;
                    }
                    setExportStatus('Memilih lokasi penyimpanan…');
                    const result = await window.pywebview.api.export_diagnostic_logs(json);
                    if (result && result.success) {
                        const where = result.path || '';
                        setExportStatus((result.fallback ? 'Dialog simpan tidak tersedia, log disimpan otomatis di: ' : 'Log disimpan di: ') + where);
                        showConnectionNotice('info', '📄 Log debug disimpan.', 6000);
                    } else if (result && result.cancelled) {
                        setExportStatus('Ekspor dibatalkan.');
                    } else {
                        setExportStatus('Gagal ekspor log: ' + ((result && result.error) || 'penyebab tidak diketahui'), true);
                        showConnectionNotice('issue', 'Gagal ekspor log.', 6000);
                    }
                    return;
                }
                if (window.AndroidBridge?.exportDiagnosticLogs) {
                    window.AndroidBridge.exportDiagnosticLogs(json);
                    return;
                }
                const blob = new Blob([json], {type: 'application/json;charset=utf-8'});
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = 'ira-zte-diagnostic-' + new Date().toISOString().replace(/[:.]/g, '-') + '.json';
                link.click();
                setTimeout(() => URL.revokeObjectURL(url), 1000);
            } catch (error) {
                setExportStatus('Gagal ekspor log: ' + String(error), true);
                showConnectionNotice('issue', 'Gagal ekspor log: ' + String(error), 8000);
            }
        }

        async function fetchTelemetry() {
            const connEl = document.getElementById('status-conn');
            const setConnectionStatus = (message, failed = false) => {
                connEl.innerText = message;
                connEl.className = failed
                    ? "text-[11px] font-medium bg-red-950/40 border border-red-500/30 text-red-400 px-3 py-1 rounded-xl shadow-inner"
                    : "text-[11px] font-medium bg-slate-900 border border-slate-800 px-3 py-1 rounded-xl text-slate-400 shadow-inner";
            };
            try {
                if (!window.pywebview || !window.pywebview.api || typeof window.pywebview.api.get_router_data !== 'function') {
                    throw new Error('Bridge pywebview belum siap / API get_router_data tidak tersedia');
                }
                // A broken WebView bridge can leave a Promise pending forever. Race it against
                // a timeout so the UI reports the failure and polling can retry on the next tick.
                const res = await Promise.race([
                    window.pywebview.api.get_router_data(),
                    new Promise((_, reject) => setTimeout(
                        () => reject(new Error('Timeout menunggu respons API desktop (15 detik)')),
                        15000
                    ))
                ]);
                if (res && typeof res === 'object' && Object.keys(res).length > 0) {
                    updateUI(res);
                } else {
                    updateUI({ signalbar: "0", internet_ok: false });
                    setConnectionStatus('Router tidak merespons', true);
                }
            } catch (err) {
                console.error("Gagal ambil data:", err);
                updateUI({ signalbar: "0", internet_ok: false });
                setConnectionStatus('Gagal membaca telemetry: ' + String(err?.message || err), true);
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

    @staticmethod
    def _default_export_dir():
        home = Path.home()
        for name in ("Downloads", "Documents"):
            candidate = home / name
            if candidate.is_dir():
                return candidate
        return home

    def export_diagnostic_logs(self, payload):
        """Save a user-requested, sanitized diagnostic report as a JSON file.

        Uses pywebview's own save dialog, which is safe to call from the JS API thread
        (a separate tkinter root is not). If the dialog is unavailable or fails, the report
        is written to the Downloads/Documents folder so the export never fails silently.
        """
        import json
        try:
            text = json.dumps(json.loads(payload), ensure_ascii=False, indent=2)
        except Exception as e:
            return {"success": False, "error": f"Data log tidak valid: {type(e).__name__}: {e}"}

        filename = f"ira-zte-diagnostic-{time.strftime('%Y%m%d-%H%M%S')}.json"
        chosen = None
        try:
            windows = getattr(webview, "windows", None) or []
            if not windows:
                raise RuntimeError("Jendela aplikasi belum siap")
            dialog_type = webview.FileDialog.SAVE if hasattr(webview, "FileDialog") else webview.SAVE_DIALOG
            result = windows[0].create_file_dialog(
                dialog_type,
                directory=str(self._default_export_dir()),
                save_filename=filename,
                file_types=("JSON (*.json)", "Semua file (*.*)"),
            )
            if not result:
                return {"success": False, "cancelled": True}
            chosen = Path(result if isinstance(result, (str, os.PathLike)) else result[0])
            if not chosen.suffix:
                chosen = chosen.with_suffix(".json")
        except Exception as e:
            print(f"[ERROR EXPORT LOG] dialog: {type(e).__name__}: {e}")
            chosen = None

        used_fallback = chosen is None
        if used_fallback:
            chosen = self._default_export_dir() / filename
        try:
            chosen.parent.mkdir(parents=True, exist_ok=True)
            chosen.write_text(text, encoding="utf-8")
        except Exception as e:
            print(f"[ERROR EXPORT LOG] write: {type(e).__name__}: {e}")
            return {"success": False, "error": f"Tidak bisa menulis file: {type(e).__name__}: {e}"}
        return {"success": True, "path": str(chosen), "fallback": used_fallback}

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
            # The EXE workflow publishes BOTH a Portable EXE and a Setup installer.
            # Only the portable EXE can be swapped in place by the updater; the
            # installer must never replace the running executable.
            matches = [
                asset for asset in assets
                if isinstance(asset, dict)
                and name_of(asset).lower().endswith(".exe")
                and "ira_zte_live_signal_charts" in name_of(asset).lower()
                and "setup" not in name_of(asset).lower()
                and "installer" not in name_of(asset).lower()
            ]
            # Prefer the explicit "-Portable-" asset, then legacy single-EXE naming.
            matches.sort(key=lambda asset: 0 if "portable" in name_of(asset).lower() else 1)
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

    # --- Unduhan update: beberapa koneksi paralel (HTTP Range) -----------------------------
    # CDN GitHub sering membatasi kecepatan per koneksi; memakai beberapa koneksi sekaligus
    # biasanya jauh lebih cepat. Jika server tidak mendukung Range atau unduhan paralel gagal,
    # otomatis kembali ke unduhan satu koneksi.
    _UPDATE_CONNECTIONS = 4
    _UPDATE_BLOCK_SIZE = 4 * 1024 * 1024
    _UPDATE_PARALLEL_MIN_SIZE = 2 * 1024 * 1024

    @staticmethod
    def _probe_download(url, headers):
        """Return (total_bytes, final_url, supports_range) without downloading the body."""
        with requests.get(url, headers={**headers, "Range": "bytes=0-0"}, stream=True, timeout=(5, 15)) as response:
            response.raise_for_status()
            final_url = response.url
            if response.status_code == 206:
                tail = response.headers.get("Content-Range", "").rsplit("/", 1)[-1]
                total = int(tail) if tail.isdigit() else 0
                return total, final_url, total > 0
            return int(response.headers.get("Content-Length") or 0), final_url, False

    def _report_download(self, downloaded, total, started_at):
        elapsed = max(time.monotonic() - started_at, 0.001)
        speed = downloaded / elapsed
        eta = max((total - downloaded) / speed, 0) if total > 0 and speed > 0 else None
        percent = min(downloaded * 100 / total, 100) if total > 0 else 0
        self._set_update_progress(
            downloaded=downloaded, total=total, speed_bps=round(speed),
            eta_seconds=round(eta) if eta is not None else None,
            percent=round(percent, 1), status="Mengunduh update…",
        )

    def _download_single(self, url, headers, started_at):
        downloaded = 0
        chunks = []
        with requests.get(url, headers=headers, timeout=(5, 60), stream=True) as response:
            response.raise_for_status()
            total = int(response.headers.get("Content-Length") or 0)
            self._set_update_progress(total=total, status="Mengunduh update…")
            for chunk in response.iter_content(chunk_size=256 * 1024):
                if not chunk:
                    continue
                chunks.append(chunk)
                downloaded += len(chunk)
                self._report_download(downloaded, total, started_at)
        return b"".join(chunks)

    def _download_parallel(self, url, total, headers, started_at):
        import threading
        from collections import deque

        block = self._UPDATE_BLOCK_SIZE
        pending = deque((start, min(start + block, total) - 1) for start in range(0, total, block))
        buffer = bytearray(total)
        view = memoryview(buffer)
        lock = threading.Lock()
        state = {"downloaded": 0, "error": None}
        self._set_update_progress(total=total, status="Mengunduh update…")

        def worker():
            session = requests.Session()
            try:
                while True:
                    with lock:
                        if state["error"] is not None or not pending:
                            return
                        start, end = pending.popleft()
                    for attempt in range(3):
                        counted = 0
                        try:
                            with session.get(url, headers={**headers, "Range": f"bytes={start}-{end}"},
                                             stream=True, timeout=(5, 20)) as response:
                                if response.status_code != 206:
                                    raise RuntimeError(f"Server tidak mendukung Range (HTTP {response.status_code})")
                                position = start
                                for chunk in response.iter_content(chunk_size=64 * 1024):
                                    if not chunk:
                                        continue
                                    if position + len(chunk) > end + 1:
                                        raise RuntimeError("Server mengirim data melebihi rentang yang diminta")
                                    view[position:position + len(chunk)] = chunk
                                    position += len(chunk)
                                    counted += len(chunk)
                                    with lock:
                                        state["downloaded"] += len(chunk)
                                if position != end + 1:
                                    raise RuntimeError("Rentang data tidak lengkap")
                            break
                        except Exception as e:
                            with lock:
                                state["downloaded"] -= counted
                                if attempt == 2:
                                    if state["error"] is None:
                                        state["error"] = e
                                    return
                            time.sleep(0.5 * (attempt + 1))
            finally:
                session.close()

        workers = [threading.Thread(target=worker, daemon=True)
                   for _ in range(max(1, min(self._UPDATE_CONNECTIONS, len(pending))))]
        for thread in workers:
            thread.start()
        while any(thread.is_alive() for thread in workers):
            with lock:
                done = state["downloaded"]
            self._report_download(done, total, started_at)
            time.sleep(0.25)
        for thread in workers:
            thread.join()
        if state["error"] is not None:
            raise state["error"]
        if state["downloaded"] != total:
            raise RuntimeError(f"Ukuran unduhan tidak sesuai ({state['downloaded']} dari {total} byte)")
        self._report_download(total, total, started_at)
        return bytes(buffer)

    def _download_asset(self, url):
        headers = {"User-Agent": "IRA-ZTE-Live-Signal-Charts", "Accept-Encoding": "identity"}
        started_at = time.monotonic()
        try:
            total, final_url, ranged = self._probe_download(url, headers)
        except Exception as e:
            print(f"[UPDATE] probe unduhan gagal, memakai unduhan standar: {type(e).__name__}: {e}")
            total, final_url, ranged = 0, url, False
        if ranged and total >= self._UPDATE_PARALLEL_MIN_SIZE:
            try:
                return self._download_parallel(final_url, total, headers, started_at)
            except Exception as e:
                print(f"[UPDATE] unduhan paralel gagal, memakai unduhan standar: {type(e).__name__}: {e}")
                self._set_update_progress(downloaded=0, percent=0, status="Mencoba unduhan standar…")
                started_at = time.monotonic()
        return self._download_single(url, headers, started_at)

    # --- Jalankan saat Windows dimulai (khusus EXE hasil instalasi) --------------------
    _STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
    _STARTUP_VALUE = "IRA ZTE Live Signal Charts"

    @staticmethod
    def _installed_exe_path():
        """Path EXE hasil instalasi (folder berisi unins000.exe milik Inno Setup).

        Mengembalikan None untuk versi portable atau saat dijalankan dari kode sumber (.py),
        sehingga opsi startup tidak muncul di sana.
        """
        if platform.system().lower() != "windows" or not getattr(sys, "frozen", False):
            return None
        exe = Path(sys.executable)
        return exe if (exe.parent / "unins000.exe").is_file() else None

    def get_startup_status(self):
        exe = self._installed_exe_path()
        if exe is None:
            return {"supported": False, "enabled": False,
                    "reason": "Opsi ini hanya tersedia pada aplikasi hasil instalasi (installer)."}
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self._STARTUP_KEY, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, self._STARTUP_VALUE)
            enabled = os.path.normcase(str(value).strip().strip('"')) == os.path.normcase(str(exe))
        except FileNotFoundError:
            enabled = False
        except Exception as e:
            return {"supported": True, "enabled": False, "error": f"{type(e).__name__}: {e}"}
        return {"supported": True, "enabled": enabled, "path": str(exe)}

    def set_startup(self, enabled):
        exe = self._installed_exe_path()
        if exe is None:
            return {"success": False, "error": "Opsi ini hanya tersedia pada aplikasi hasil instalasi."}
        try:
            import winreg
            if enabled:
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, self._STARTUP_KEY) as key:
                    winreg.SetValueEx(key, self._STARTUP_VALUE, 0, winreg.REG_SZ, f'"{exe}"')
            else:
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self._STARTUP_KEY, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.DeleteValue(key, self._STARTUP_VALUE)
                except FileNotFoundError:
                    pass
        except Exception as e:
            return {"success": False, "error": f"{type(e).__name__}: {e}"}
        return {"success": True, "enabled": bool(enabled)}

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
                "asset_size": int(asset.get("size") or 0) if asset else 0,
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

            if app_kind == "exe":
                writable, reason = self._exe_dir_writable()
                if not writable:
                    return {"success": False, "error": reason}

            self._set_update_progress(active=True, percent=0, downloaded=0, total=0,
                                      speed_bps=0, eta_seconds=None, status="Menghubungkan ke server…", error=None)
            try:
                payload = self._download_asset(asset["browser_download_url"])
                self._set_update_progress(active=False, percent=100, downloaded=len(payload), total=len(payload),
                                          status="Unduhan selesai, memvalidasi file…")
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
            batch_path = current_exe.with_name(current_exe.stem + "_update.bat")
            # Real CRLF line breaks are required. The previous version wrote the literal
            # text "\r\n", so cmd.exe saw one broken line, never replaced the EXE and
            # never relaunched the app after it exited.
            batch_lines = [
                "@echo off",
                "set TRIES=0",
                ":retry",
                "ping 127.0.0.1 -n 3 >nul",
                f'move /y "{temp_exe}" "{current_exe}" >nul 2>&1',
                "if not errorlevel 1 goto done",
                "set /a TRIES+=1",
                "if %TRIES% lss 20 goto retry",
                "exit /b 1",
                ":done",
                "set PYINSTALLER_RESET_ENVIRONMENT=1",
                "set _MEIPASS2=",
                f'start "" "{current_exe}"',
                'del "%~f0"',
            ]
            batch_path.write_text("\r\n".join(batch_lines) + "\r\n", encoding="utf-8")
            # Do not leak PyInstaller's onefile temp-dir variables into the relaunched app.
            child_env = {k: v for k, v in os.environ.items() if not k.startswith(("_MEI", "_PYI"))}
            child_env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
            subprocess.Popen(
                ["cmd.exe", "/c", str(batch_path)],
                cwd=str(current_exe.parent),
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                close_fds=True,
                env=child_env,
            )
            os._exit(0)
        except Exception as e:
            self._set_update_progress(active=False, status="Pembaruan gagal.", error=f"{type(e).__name__}: {e}")
            return {"success": False, "error": f"Pembaruan gagal: {type(e).__name__}: {e}"}

    @staticmethod
    def _exe_dir_writable():
        """Check that the EXE can be replaced in place (fails in Program Files without admin)."""
        exe_dir = Path(sys.executable).parent
        try:
            probe = exe_dir / ".ira_write_test.tmp"
            probe.write_bytes(b"ok")
            probe.unlink()
            return True, ""
        except OSError as e:
            return False, (
                f"Folder instalasi ({exe_dir}) tidak bisa ditulis tanpa hak admin ({type(e).__name__}). "
                "Pasang ulang aplikasi dengan installer terbaru (per-pengguna) atau pindahkan EXE portable ke folder biasa."
            )

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
        endpoint = SPEED_TEST_ENDPOINT
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
