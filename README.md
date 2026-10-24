# IRA ZTE MC8501 5G Live Signal Charts

Aplikasi desktop untuk memantau telemetri sinyal 5G dari router **ZTE MC8501** secara langsung. Antarmuka dibuat menggunakan Python dengan dashboard HTML/JavaScript tertanam, termasuk grafik langsung untuk berbagai metrik sinyal radio.

> [!PENTING]
> **PENAFIAN, STATUS INDEPENDEN, DAN BATASAN PENGGUNAAN**
>
> Proyek ini merupakan proyek **independen untuk eksperimen, pemantauan, dan penggunaan pribadi**. Repositori ini **tidak berafiliasi, tidak disponsori, tidak didukung, tidak dikelola, dan tidak mewakili** merek, perusahaan, badan usaha, penyedia layanan internet, atau organisasi mana pun.
>
> Secara khusus, proyek ini **bukan produk resmi, bukan aplikasi resmi, dan bukan bagian dari IRA Internet Rakyat maupun PT. Telemedia Komunikasi Pratama**. Penyebutan nama “IRA”, “Internet Rakyat”, “ZTE”, “MC8501”, atau nama dan merek lain di dalam repositori ini hanya digunakan untuk menjelaskan konteks teknis, perangkat yang kompatibel, atau lingkungan pengujian. Penyebutan tersebut tidak menyatakan adanya hubungan bisnis, kemitraan, dukungan, persetujuan, atau pengesahan dari pemilik merek atau pihak terkait.
>
> Aplikasi ini dibuat dan dipelihara secara mandiri oleh pengembang repositori ini. Aplikasi ini tidak dimaksudkan untuk menjadi kanal dukungan pelanggan, alat resmi penyedia layanan, aplikasi konfigurasi resmi, atau pengganti perangkat lunak maupun layanan yang disediakan oleh produsen perangkat dan penyedia layanan internet.
>
> **Gunakan dengan risiko sendiri.** Tidak ada jaminan bahwa aplikasi akan selalu berfungsi, kompatibel dengan setiap versi firmware, akurat untuk setiap konfigurasi jaringan, atau tersedia tanpa gangguan. Pengembang proyek ini tidak bertanggung jawab atas gangguan layanan, kehilangan data, perubahan konfigurasi, kerusakan perangkat, atau konsekuensi lain yang timbul dari penggunaan, ketidakmampuan menggunakan, modifikasi, maupun penyalahgunaan aplikasi, sejauh diizinkan oleh hukum yang berlaku.
>
> Pengguna bertanggung jawab memastikan bahwa penggunaan aplikasi dan akses ke perangkat/router yang dipantau telah mendapat izin yang sesuai serta mematuhi ketentuan layanan, kebijakan jaringan, dan hukum yang berlaku. Jangan gunakan aplikasi untuk mengakses perangkat atau jaringan milik pihak lain tanpa izin.
>
> Nama, logo, merek dagang, dan hak kekayaan intelektual pihak ketiga tetap menjadi milik masing-masing pemiliknya. Repositori ini tidak mengklaim kepemilikan atas merek atau aset pihak ketiga tersebut. Jika pemilik hak menemukan materi yang perlu diklarifikasi atau ditinjau, silakan ajukan laporan melalui kanal Issues di GitHub.

Aplikasi saat ini dikonfigurasi untuk mengakses router melalui `http://192.168.0.1`. Jika alamat IP lokal router berbeda, sesuaikan alamat tersebut di `router_app.py`.

<img width="1084" height="792" alt="Tampilan IRA ZTE MC8501 5G Live Signal Charts" src="https://github.com/user-attachments/assets/de1c79b4-055d-42e5-abd8-5003385a4fb9" />
<img width="1081" height="757" alt="Tampilan dashboard dan grafik sinyal" src="https://github.com/user-attachments/assets/2fdc4022-4dec-43ed-b3fe-48f25b56d035" />

## Fitur

- **Grafik sinyal 5G secara langsung:**
  - **RSRP** — daya sinyal yang diterima.
  - **RSSI** — kekuatan sinyal total yang diterima.
  - **RSRQ** — kualitas sinyal.
  - **SINR / SNR** — kualitas sinyal relatif terhadap derau dan interferensi.
- **Informasi router dan jaringan secara langsung**, meliputi:
  - Status koneksi ke menara seluler.
  - Status koneksi internet.
  - PCI dan Cell ID sel 5G.
  - Jenis jaringan, tingkat indikator sinyal, dan pita frekuensi aktif.
- **Label kualitas sinyal** dari *Mantap* hingga *Buruk*, berdasarkan ambang batas yang digunakan dashboard.
- **Riwayat kejadian koneksi** untuk perubahan status menara seluler dan internet selama sesi aplikasi berlangsung.
- **Pengaturan dashboard** untuk tema gelap/terang dan interval pembaruan telemetri (1, 2, atau 4 detik).
- Antarmuka ringkas menggunakan **Tailwind CSS** dan **Chart.js**.

## Persyaratan

- Windows atau platform desktop lain yang didukung oleh [pywebview](https://pywebview.flowrl.com/).
- Python 3.9 atau versi lebih baru (disarankan).
- Router ZTE MC8501 yang dapat diakses dari komputer tempat aplikasi dijalankan.
- Koneksi internet untuk memuat pustaka antarmuka dari CDN eksternal.

Paket Python yang digunakan:

- `requests`
- `pywebview`
- `urllib3`

## Instalasi

Pilih kanal rilis sesuai kebutuhan. **Stable** direkomendasikan untuk penggunaan sehari-hari, sedangkan **Beta** berisi versi pengujian yang mungkin masih memiliki bug.

<p align="center">
  <a href="https://github.com/TheKingTermux/ira-zte-live-signal-charts/releases/latest"><img src="https://img.shields.io/badge/Unduh-Stable%20Rilis-1976D2?style=for-the-badge&logo=github&logoColor=white" alt="Unduh Stable Rilis"></a>
  &nbsp;
  <a href="https://github.com/TheKingTermux/ira-zte-live-signal-charts/releases"><img src="https://img.shields.io/badge/Unduh-Beta%20Rilis-8E44AD?style=for-the-badge&logo=github&logoColor=white" alt="Unduh Beta Rilis"></a>
</p>

- **[Stable Rilis — versi stabil terbaru](https://github.com/TheKingTermux/ira-zte-live-signal-charts/releases/latest):** pilih ini jika mengutamakan versi yang ditandai sebagai rilis stabil.
- **[Beta Rilis — semua rilis termasuk versi prarilis](https://github.com/TheKingTermux/ira-zte-live-signal-charts/releases):** buka daftar rilis lalu pilih versi beta/prarilis terbaru.

### Pilih berkas sesuai perangkat

Pada halaman rilis yang dipilih, unduh **hanya berkas yang sesuai dengan jenis aplikasi** yang ingin digunakan:

| Jenis aplikasi | Berkas yang perlu diunduh | Keterangan |
| --- | --- | --- |
| Windows | Berkas `.exe` | Aplikasi Windows siap dijalankan; tidak perlu memasang Python secara terpisah. |
| Python | Berkas `.py` (misalnya `router_app.py`) | Jalankan dengan Python setelah memasang dependensi yang dibutuhkan. |
| Android | Berkas `.apk` | Pasang pada perangkat Android yang kompatibel. |

Jangan mengunduh berkas dari kanal lain jika ingin tetap menggunakan versi yang sama. Pastikan nama versi/tag rilis cocok dengan versi yang ingin digunakan. Jika suatu jenis berkas tidak tersedia pada rilis tersebut, periksa rilis lain atau gunakan metode menjalankan dari kode sumber di bawah.

### Menjalankan dari kode sumber

Jika ingin menjalankan versi Python langsung dari repositori:

1. **Klon repositori**
   
   ```bash
   git clone https://github.com/TheKingTermux/ira-zte-live-signal-charts.git
   cd ira-zte-live-signal-charts
   ```

2. **Buat dan aktifkan lingkungan virtual** (disarankan).

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

3. **Pasang dependensi**

   ```bash
   python -m pip install requests pywebview urllib3
   ```

## Menjalankan aplikasi

Jalankan perintah berikut dari direktori repositori:

```bash
python router_app.py
```

Aplikasi akan membuka jendela desktop yang dapat diubah ukurannya dengan judul **IRA ZTE MC8501 5G LIVE SIGNAL CHARTS**.

## Konfigurasi

Alamat endpoint router saat ini ditentukan di `router_app.py`:

```python
url = f"http://192.168.0.1/ubus/?t={int(time.time() * 1000)}"
```

Jika alamat IP pengelolaan router berbeda, sesuaikan endpoint serta header `Referer` dan `Origin` yang terkait agar cocok dengan alamat router. Implementasi saat ini menggunakan endpoint `zte_nwinfo_api` / `nwinfo_get_netinfo` milik router. Karena itu, aplikasi dirancang untuk antarmuka internal router ZTE tersebut dan **bukan dashboard universal untuk semua jenis router**.

Pengaturan **Frekuensi Update Data** mengubah interval pengambilan data menjadi 1, 2, atau 4 detik.

## Referensi metrik sinyal

Dashboard menggunakan ambang batas berikut untuk memberi label kualitas sinyal:

| Metrik | Mantap | Bagus | Cukup | Buruk |
| --- | ---: | ---: | ---: | ---: |
| RSRP | ≥ -80 dBm | -81 hingga -95 dBm | -96 hingga -110 dBm | < -110 dBm |
| RSSI | ≥ -70 dBm | -71 hingga -85 dBm | -86 hingga -100 dBm | < -100 dBm |
| RSRQ | ≥ -10 dB | -11 hingga -15 dB | -16 hingga -20 dB | < -20 dB |
| SINR / SNR | ≥ 20 dB | 10 hingga 19 dB | 0 hingga 9 dB | < 0 dB |

Ambang batas tersebut merupakan acuan bawaan untuk membantu membaca kondisi sinyal secara cepat, bukan jaminan kualitas layanan atau ukuran universal untuk setiap jaringan.

## Pemecahan masalah

- **Dashboard terus menampilkan “Menghubungkan…” atau “Terputus…”**
  - Pastikan komputer dapat membuka halaman pengelolaan router.
  - Pastikan alamat IP router di `router_app.py` sudah benar.
  - Periksa apakah endpoint API lokal router dapat diakses dari komputer.
- **Nilai sinyal tidak tersedia atau ditampilkan sebagai `-`**
  - Pastikan router terhubung ke jaringan seluler dan respons telemetrinya memuat kolom 5G yang diharapkan.
- **Tata letak dashboard atau grafik tidak muncul**
  - Periksa koneksi internet karena Tailwind CSS dan Chart.js dimuat dari CDN eksternal.

## Keamanan dan privasi

- Aplikasi berkomunikasi dengan endpoint pengelolaan lokal router menggunakan **HTTP**, bukan HTTPS.
- Implementasi saat ini menonaktifkan peringatan keamanan permintaan urllib3 dan menggunakan verifikasi TLS yang dinonaktifkan pada permintaan router. Hal ini perlu ditinjau kembali jika kode diadaptasi untuk HTTPS.
- Jalankan aplikasi hanya di jaringan lokal yang tepercaya. **Jangan paparkan antarmuka pengelolaan router ke internet publik.**
- Riwayat koneksi disimpan di memori browser selama sesi aplikasi berjalan dan akan dihapus saat aplikasi dimulai ulang atau ketika riwayat dibersihkan.
- Jangan membagikan tangkapan layar, log, atau berkas konfigurasi yang dapat mengungkap alamat jaringan, identitas perangkat, atau informasi pribadi tanpa memeriksanya terlebih dahulu.

## Status proyek

Proyek ini terutama ditujukan untuk pemantauan pribadi router ZTE MC8501. Perubahan firmware dapat memengaruhi endpoint internal maupun kolom telemetri yang dikembalikan perangkat. Proyek ini dikelola secara independen dan bukan perangkat lunak resmi dari produsen router atau penyedia layanan internet.

## Lisensi dan penggunaan ulang

Repositori ini belum menetapkan lisensi perangkat lunak. Sampai lisensi ditambahkan, **jangan menganggap kode atau materi di repositori ini bebas digunakan ulang, dimodifikasi, atau didistribusikan ulang**. Hak atas merek dagang dan aset pihak ketiga tetap berada pada pemilik masing-masing.

---

Jika menemukan masalah atau ingin mengusulkan perubahan, silakan gunakan [Issues](https://github.com/TheKingTermux/ira-zte-live-signal-charts/issues). Harap diingat bahwa repositori ini merupakan proyek independen; kanal tersebut bukan layanan dukungan resmi IRA Internet Rakyat, PT. Telemedia Komunikasi Pratama, atau ZTE.
