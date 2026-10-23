# IRA ZTE MC8501 5G Live Signal Charts

A lightweight desktop dashboard for monitoring live 5G signal telemetry from the **ZTE MC8501** router. The interface is built with Python and an embedded HTML/JavaScript dashboard, with live charts for key radio-signal metrics.

> **Personal-use project.** The application is currently configured for a router reachable at `http://192.168.0.1`. Update the address in `router_app.py` if your router uses a different LAN IP.

<img width="1084" height="792" alt="2026-10-24 00_15_23-IRA ZTE MC8501 5G LIVE SIGNAL CHARTS" src="https://github.com/user-attachments/assets/de1c79b4-055d-42e5-abd8-5003385a4fb9" />
<img width="1081" height="757" alt="2026-10-24 00_34_17-IRA ZTE MC8501 5G LIVE SIGNAL CHARTS" src="https://github.com/user-attachments/assets/2fdc4022-4dec-43ed-b3fe-48f25b56d035" />


## Features

- **Live 5G signal charts** for:
  - **RSRP** — received signal power
  - **RSSI** — total received signal strength
  - **RSRQ** — signal quality
  - **SINR / SNR** — signal quality relative to noise and interference
- **Live router and network information**, including:
  - Tower connection status
  - Internet connectivity status
  - 5G Cell PCI and Cell ID
  - Network type, signal-bar level, and active band
- **Signal-quality labels** ranging from *Mantap* (excellent) to *Buruk* (poor), based on the thresholds shown in the dashboard.
- **Connection event history** for tower and internet status changes during the current session.
- **Dashboard settings** for dark/light theme and telemetry refresh interval (1, 2, or 4 seconds).
- Compact dashboard built with **Tailwind CSS** and **Chart.js**.

## Requirements

- Windows or another desktop platform supported by [pywebview](https://pywebview.flowrl.com/)
- Python 3.9 or newer recommended
- A ZTE MC8501 router accessible from the computer running the application
- Internet access for loading the dashboard's CDN-hosted frontend libraries

Python packages used by the application:

- `requests`
- `pywebview`
- `urllib3`

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/TheKingTermux/ira-zte-live-signal-charts.git
   cd ira-zte-live-signal-charts
   ```

2. **Create and activate a virtual environment** (recommended)

   Windows:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   Linux/macOS:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   python -m pip install requests pywebview urllib3
   ```

## Run

Start the dashboard from the repository directory:

```bash
python router_app.py
```

The application opens a resizable desktop window titled **IRA ZTE MC8501 5G LIVE SIGNAL CHARTS**.

## Configuration

The router endpoint is currently defined in `router_app.py`:

```python
url = f"http://192.168.0.1/ubus/?t={int(time.time() * 1000)}"
```

If the router's management IP differs, update the endpoint and the related `Referer` and `Origin` headers to match your router's address. The current implementation queries the router's `zte_nwinfo_api` / `nwinfo_get_netinfo` endpoint, so it is designed around the ZTE router's existing interface rather than being a generic router dashboard.

The dashboard's **Frekuensi Update Data** setting changes the polling interval to 1, 2, or 4 seconds.

## Signal metric reference

The dashboard uses the following thresholds to label signal quality:

| Metric | Mantap | Bagus | Cukup | Buruk |
| --- | ---: | ---: | ---: | ---: |
| RSRP | ≥ -80 dBm | -81 to -95 dBm | -96 to -110 dBm | < -110 dBm |
| RSSI | ≥ -70 dBm | -71 to -85 dBm | -86 to -100 dBm | < -100 dBm |
| RSRQ | ≥ -10 dB | -11 to -15 dB | -16 to -20 dB | < -20 dB |
| SINR / SNR | ≥ 20 dB | 10 to 19 dB | 0 to 9 dB | < 0 dB |

These are the dashboard's built-in reference thresholds and are intended as a quick visual guide.

## Troubleshooting

- **The dashboard stays on “Menghubungkan…” or shows “Terputus…”**
  - Make sure the computer can open the router's management interface.
  - Confirm that the router IP in `router_app.py` is correct.
  - Check that the router's local API endpoint is reachable from your computer.
- **Signal values are missing or displayed as `-`**
  - Confirm that the router is connected to the mobile network and that its telemetry response contains the expected 5G fields.
- **The dashboard layout or charts do not load**
  - Check your internet connection, because Tailwind CSS and Chart.js are loaded from external CDNs.

## Security and privacy notes

- The application communicates with the router's local management endpoint over **HTTP**, not HTTPS.
- The current code disables urllib3's insecure-request warning and sends the router request with TLS verification disabled; this is relevant only to the current HTTP/router request implementation and should be reviewed before adapting it to HTTPS.
- Run this tool only on a trusted local network and do not expose the router management interface to the public internet.
- The connection history is stored in browser memory for the current application session and is cleared when the app restarts or when you clear the history.

## Project status

This project is primarily intended for personal monitoring of a ZTE MC8501 router. Router firmware changes may affect the internal endpoint or the telemetry fields returned by the device.

## License

No license has been specified in this repository yet. Unless a license is added, reuse and redistribution are not automatically granted.
