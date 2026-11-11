# IRA ZTE MC8501 5G Live Signal Charts

Aplikasi Desktop dan Android untuk memantau telemetri jaringan **ZTE MC8501 5G** secara langsung. Dashboard menampilkan metrik radio, status router dan internet, grafik ping, riwayat koneksi, serta berbagai alat diagnostik dan pembaruan aplikasi.

<p align="center">
  <a href="#instalasi"><img src="https://img.shields.io/badge/Unduh-1976D2?style=for-the-badge&logo=github&logoColor=white" alt="Unduh"></a>
  <a href="https://github.com/TheKingTermux/ira-zte-live-signal-charts/releases"><img src="https://img.shields.io/github/v/release/TheKingTermux/ira-zte-live-signal-charts?include_prereleases&label=Release" alt="GitHub Release"></a>
</p>

> [!IMPORTANT]
> **PENAFIAN, STATUS INDEPENDEN, DAN BATASAN PENGGUNAAN**
>
> Proyek ini merupakan proyek **independen untuk eksperimen, pemantauan, dan penggunaan pribadi**. Repositori ini **tidak berafiliasi, tidak disponsori, tidak didukung, tidak dikelola, dan tidak mewakili** merek, perusahaan, badan usaha, penyedia layanan internet, atau organisasi mana pun.
>
> Secara khusus, proyek ini **bukan produk resmi, bukan aplikasi resmi, dan bukan bagian dari IRA (Internet Rakyat), ZTE Corporation maupun PT. Telemedia Komunikasi Pratama**. Penyebutan nama “IRA”, “Internet Rakyat”, “ZTE”, “MC8501”, atau nama dan merek lain di dalam repositori ini hanya digunakan untuk menjelaskan konteks teknis, perangkat yang kompatibel, atau lingkungan pengujian. Penyebutan tersebut tidak menyatakan adanya hubungan bisnis, kemitraan, dukungan, persetujuan, atau pengesahan dari pemilik merek atau pihak terkait.
>
> Aplikasi ini dibuat dan dipelihara secara mandiri oleh pengembang repositori ini. Aplikasi ini tidak dimaksudkan untuk menjadi kanal dukungan pelanggan, alat resmi penyedia layanan, aplikasi konfigurasi resmi, atau pengganti perangkat lunak maupun layanan yang disediakan oleh produsen perangkat dan penyedia layanan internet.
>
> **Gunakan dengan risiko sendiri.** Tidak ada jaminan bahwa aplikasi akan selalu berfungsi, kompatibel dengan setiap versi firmware, akurat untuk setiap konfigurasi jaringan, atau tersedia tanpa gangguan. Pengembang proyek ini tidak bertanggung jawab atas gangguan layanan, kehilangan data, perubahan konfigurasi, kerusakan perangkat, atau konsekuensi lain yang timbul dari penggunaan, ketidakmampuan menggunakan, modifikasi, maupun penyalahgunaan aplikasi, sejauh diizinkan oleh hukum yang berlaku.
>
> Pengguna bertanggung jawab memastikan bahwa penggunaan aplikasi dan akses ke perangkat/router yang dipantau telah mendapat izin yang sesuai serta mematuhi ketentuan layanan, kebijakan jaringan, dan hukum yang berlaku. Jangan gunakan aplikasi untuk mengakses perangkat atau jaringan milik pihak lain tanpa izin.
>
> Nama, logo, merek dagang, dan hak kekayaan intelektual pihak ketiga tetap menjadi milik masing-masing pemiliknya. Repositori ini tidak mengklaim kepemilikan atas merek atau aset pihak ketiga tersebut. Jika pemilik hak menemukan materi yang perlu diklarifikasi atau ditinjau, silakan ajukan laporan melalui kanal Issues di GitHub.

## Daftar Isi

- [Fitur](#fitur)
- [Tampilan Aplikasi](#tampilan-aplikasi)
- [Kompatibilitas dan Persyaratan](#kompatibilitas-dan-persyaratan)
- [Instalasi](#instalasi)
- [Menjalankan dari Kode Sumber](#menjalankan-dari-kode-sumber)
- [Panduan Penggunaan](#panduan-penggunaan)
- [Konfigurasi Router](#konfigurasi-router)
- [Referensi Metrik Sinyal](#referensi-metrik-sinyal)
- [Pemecahan Masalah](#pemecahan-masalah)
- [Keamanan dan Privasi](#keamanan-dan-privasi)
- [Pengembangan dan Build](#pengembangan-dan-build)
- [Status Proyek](#status-proyek)
- [Lisensi dan Penggunaan Ulang](#lisensi-dan-penggunaan-ulang)

## Fitur

### 1. Dashboard dan pemantauan sinyal

- **Grafik sinyal 5G secara langsung:**
  - **RSRP** — daya sinyal referensi yang diterima.
  - **RSSI** — kekuatan sinyal total yang diterima.
  - **RSRQ** — kualitas sinyal referensi.
  - **SINR / SNR** — kualitas sinyal relatif terhadap derau dan interferensi.
- **Skala sumbu grafik dinamis** agar perubahan nilai kecil tetap mudah dibaca.
- **Jumlah titik grafik adaptif** untuk menyesuaikan ruang tampilan pada ukuran layar yang berbeda.
- **Grafik ping dashboard** untuk memantau latensi jaringan secara berkala.
- **Status router dan jaringan**, termasuk status koneksi ke menara seluler dan status koneksi internet.
- **Informasi seluler**, seperti PCI, Cell ID, jenis jaringan, indikator sinyal, serta pita frekuensi aktif yang tersedia dari API router.
- **Label kualitas sinyal** dari *Mantap* hingga *Buruk* berdasarkan ambang batas yang digunakan dashboard.

### 2. Diagnostik koneksi dan riwayat

- **Riwayat koneksi** untuk mencatat perubahan status koneksi menara seluler dan internet selama sesi aplikasi.
- **Notifikasi dan pop-up gangguan** ketika terjadi perubahan atau gangguan koneksi.
- Detail gangguan dan durasi kejadian ditampilkan agar kondisi koneksi lebih mudah diperiksa.
- Tersedia pengaturan untuk menyembunyikan pop-up gangguan tower dan internet secara terpisah, serta mengembalikan pengaturan pop-up ke kondisi awal.
- Banner status, suara peringatan, dan riwayat kejadian tetap dapat digunakan secara terpisah dari preferensi pop-up.
- Pemeriksaan ulang koneksi internet dapat dilakukan dari pop-up gangguan.

### 3. Ping Tools

- Ping manual ke hostname atau alamat IP yang dimasukkan pengguna.
- Validasi input untuk mencegah target kosong atau format input yang tidak sesuai.
- Menampilkan hasil ping beserta statistik **MIN, AVG, dan MAX**.
- Grafik latensi ping untuk melihat perubahan waktu respons.
- Riwayat Ping Tools manual dipisahkan dari sampel ping otomatis dashboard, sehingga keduanya tidak saling mengubah statistik atau riwayat.
- Pada Windows, proses ping dijalankan tanpa memunculkan jendela Command Prompt tambahan.
- Implementasi Android menggunakan pemanggilan ping asynchronous agar antarmuka tidak tertahan saat menunggu respons jaringan.

### 4. Speed Test

- Pengujian kecepatan **download** dan **upload**, dilengkapi pengukuran latensi.
- Menampilkan hasil pengujian serta nilai statistik yang tersedia selama proses berlangsung.
- Proses pengujian berjalan melalui antarmuka aplikasi.

> Catatan: hasil Speed Test dipengaruhi server pengujian, kondisi jaringan, perangkat, dan beban jaringan saat tes dilakukan. Kegagalan atau pembatasan dari server pengujian (misalnya HTTP 429) dapat memengaruhi hasil.

### 5. Pengaturan dan antarmuka

- Tema **gelap dan terang**.
- Pengaturan interval pembaruan telemetri: **1, 2, atau 4 detik**.
- Tampilan dashboard dan grafik menyesuaikan ukuran jendela.
- Riwayat notifikasi dan indikator status koneksi.
- Pengaturan aplikasi dikelompokkan dalam jendela Settings, termasuk bagian **General** dan **About**.
- Penyimpanan preferensi menggunakan mekanisme penyimpanan yang memiliki fallback ke memori apabila penyimpanan WebView tidak tersedia.

### 6. About dan pembaruan aplikasi

Bagian **About** menyediakan informasi versi aplikasi, tautan repositori, serta pengaturan pembaruan.

- Pilihan kanal **Stable** dan **Beta**.
- Pemeriksaan pembaruan otomatis maupun manual.
- Informasi versi dan status rilis yang tersedia.
- Tombol untuk memeriksa, mengunduh, dan memasang pembaruan.
- Indikator progres unduhan yang dapat menampilkan persentase, ukuran data yang sudah diunduh, kecepatan unduhan, dan perkiraan waktu tersisa apabila informasi ukuran berkas tersedia.
- Pemilihan aset pembaruan disesuaikan dengan jenis aplikasi yang sedang digunakan:
  - Aplikasi Windows EXE hanya mengambil aset EXE yang sesuai.
  - Aplikasi Python hanya mengambil berkas sumber Python yang sesuai.
  - Aplikasi Android hanya mengambil APK.
- Versi rilis dibandingkan berdasarkan nomor versi, bukan hanya urutan tanggal publikasi.

**Perbedaan kanal:**

| Kanal | Keterangan |
| --- | --- |
| Stable | Menggunakan rilis stabil/non-prerelease terbaru. Direkomendasikan untuk penggunaan sehari-hari. |
| Beta | Dapat menggunakan versi prerelease dan rilis stabil, lalu memilih versi dengan nomor versi tertinggi. Versi beta dapat mengandung bug. |

### 7. Ekspor log diagnostik

Fitur **Ekspor Log Debug** membantu mengumpulkan informasi saat melaporkan masalah.

Laporan JSON dapat mencakup:
- Versi aplikasi dan platform.
- Status koneksi router, tower, dan internet.
- Data telemetri dasar.
- Riwayat koneksi.
- Error JavaScript terbaru.
- Preferensi antarmuka yang tidak sensitif.

Perilaku ekspor:
- **Windows/Desktop:** menggunakan dialog penyimpanan file. Jika dialog tidak tersedia, aplikasi dapat menyimpan file ke folder Downloads, Documents, atau folder home yang tersedia.
- **Android:** membagikan laporan melalui Android Share Sheet.

Laporan diagnostik dirancang untuk **tidak menyertakan password, cookie, token, maupun kredensial router**. Meski demikian, periksa isi laporan sebelum membagikannya.

### 8. Aplikasi Android

Aplikasi Android menggunakan implementasi native Kotlin untuk fungsi yang membutuhkan integrasi sistem Android.

- Dashboard telemetri dan grafik sinyal.
- Grafik ping dashboard.
- Ping Tools manual dan statistik MIN/AVG/MAX.
- Pengaturan aplikasi dan bagian About.
- Updater APK dengan pilihan kanal Stable/Beta.
- Unduhan APK dengan indikator progres.
- Instalasi pembaruan melalui mekanisme installer Android; pengguna tetap harus menyetujui proses instalasi.
- Ekspor laporan diagnostik melalui Android Share Sheet.
- Pemanggilan data router dan ping secara asynchronous agar UI tetap responsif.

### 9. Build dan distribusi

- **Windows Portable EXE** — dapat dijalankan tanpa proses instalasi.
- **Windows Setup Installer** — memasang aplikasi ke folder pilihan, membuat shortcut Start Menu, dan menyediakan opsi shortcut Desktop.
- **Android APK** — paket aplikasi untuk perangkat Android yang kompatibel.
- Ikon aplikasi disematkan langsung ke EXE dan APK.
- Workflow rilis mendukung build kanal Stable dan Beta.
- Versi aplikasi desktop, berkas Python, dan APK diberi nomor versi rilis yang sama melalui proses version stamping.

## Tampilan Aplikasi

<p align="center">
  <img width="1087" alt="Tampilan aplikasi desktop" src="https://github.com/user-attachments/assets/0deb9917-8085-4e3d-b238-97e29c362188" />
</p>
<p align="center">
  <img width="1084" alt="Dashboard aplikasi" src="https://github.com/user-attachments/assets/de1c79b4-055d-42e5-ab8d-5003385a4fb9" />
</p>
<p align="center">
  <img width="1088" alt="Tampilan grafik dan informasi jaringan" src="https://github.com/user-attachments/assets/d0acdf62-9df2-438d-b799-e8817a2ddd19" />
</p>
<p align="center">
  <img width="1084" alt="Tampilan pengaturan aplikasi" src="https://github.com/user-attachments/assets/253c7dbd-858a-4aac-8a5f-0b3cee14728f" />
</p>
<p align="center">
  <img width="1086" alt="IRA ZTE MC8501 5G Live Signal Charts" src="https://github.com/user-attachments/assets/0ed0a05b-9b48-45e5-bc89-bbb1b4a29a86" />
</p>
<p align="center">
  <img width="1081" alt="Dashboard dan grafik sinyal" src="https://github.com/user-attachments/assets/2fdc4022-4dec-43ed-b3fe-48f25b56d035" />
</p>

## Kompatibilitas dan Persyaratan

### Windows / Desktop

- Windows 10/11 (64-bit direkomendasikan untuk paket EXE).
- Router ZTE MC8501 yang dapat diakses dari komputer tempat aplikasi dijalankan.
- Koneksi internet untuk memeriksa pembaruan, menjalankan Speed Test, dan memuat pustaka antarmuka dari CDN eksternal.
- Untuk menjalankan kode sumber: Python 3.9 atau lebih baru (versi yang digunakan workflow build dapat lebih baru).

Paket Python utama:
- `requests`
- `pywebview`
- `urllib3`

### Android

- Perangkat Android yang kompatibel dengan versi minimum SDK pada konfigurasi proyek.
- Router harus dapat dijangkau melalui jaringan lokal/Wi-Fi.
- Izin instalasi aplikasi dari sumber yang digunakan diperlukan ketika memasang pembaruan APK dari dalam aplikasi.

## Instalasi

Pilih kanal rilis sesuai kebutuhan. **Stable** direkomendasikan untuk penggunaan sehari-hari, sedangkan **Beta** berisi versi pengujian yang mungkin masih memiliki bug.

<p align="center">
  <a href="https://github.com/TheKingTermux/ira-zte-live-signal-charts/releases/latest"><img src="https://img.shields.io/badge/Unduh-Rilis%20Stable-1976D2?style=for-the-badge&logo=github&logoColor=white" alt="Unduh Rilis Stable"></a>
  &nbsp;
  <a href="https://github.com/TheKingTermux/ira-zte-live-signal-charts/releases"><img src="https://img.shields.io/badge/Unduh-Rilis%20Beta-8E44AD?style=for-the-badge&logo=github&logoColor=white" alt="Unduh Rilis Beta"></a>
</p>

- **[Rilis Stable — versi stabil terbaru](https://github.com/TheKingTermux/ira-zte-live-signal-charts/releases/latest):** pilih ini jika mengutamakan versi yang ditandai sebagai rilis stabil.
- **[Rilis Beta — semua rilis termasuk versi prarilis](https://github.com/TheKingTermux/ira-zte-live-signal-charts/releases):** buka daftar rilis lalu pilih versi beta/prarilis terbaru.

### Pilih berkas sesuai perangkat

| Jenis aplikasi | Berkas yang perlu diunduh | Keterangan |
| --- | --- | --- |
| Windows Portable | `IRA_ZTE_Live_Signal_Charts-Portable-<versi>.exe` | Jalankan langsung tanpa instalasi. |
| Windows Installer | `IRA_ZTE_Live_Signal_Charts-Setup-<versi>.exe` | Jalankan setup untuk memasang aplikasi ke folder pilihan. |
| Python | `router_app.py` | Jalankan dengan Python setelah memasang dependensi. |
| Android | Berkas `.apk` | Pasang pada perangkat Android yang kompatibel. |

Pastikan nama versi/tag rilis cocok dengan versi yang ingin digunakan. Jangan mengganti aplikasi dengan aset dari jenis platform yang berbeda.

## Menjalankan dari Kode Sumber

Jika ingin menjalankan versi Python langsung dari repositori:

1. **Klon repositori**

   ```bash
   git clone https://github.com/TheKingTermux/ira-zte-live-signal-charts.git
   cd ira-zte-live-signal-charts
   ```

2. **Buat dan aktifkan lingkungan virtual** (disarankan).

   Windows PowerShell:

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

## Menjalankan Aplikasi

Jalankan perintah berikut dari direktori repositori:

```bash
python router_app.py
```

Aplikasi akan membuka jendela desktop **IRA ZTE MC8501 5G LIVE SIGNAL CHARTS**.

## Panduan Penggunaan

1. Sambungkan komputer atau perangkat Android ke jaringan lokal yang sama dengan router.
2. Pastikan alamat pengelolaan router dapat diakses dari perangkat.
3. Jalankan aplikasi dan tunggu proses pengambilan telemetri.
4. Pantau nilai RSRP, RSSI, RSRQ, SINR, informasi sel, serta status tower dan internet dari dashboard.
5. Gunakan **Ping Tools** untuk menguji host/IP tertentu secara manual.
6. Gunakan **Speed Test** untuk menguji performa koneksi. Hasil dapat dipengaruhi kondisi jaringan dan server tes.
7. Buka **Settings → About** untuk memeriksa versi, memilih kanal pembaruan, atau mengekspor log diagnostik.

## Konfigurasi Router

Alamat endpoint router saat ini ditentukan di `router_app.py`:

```python
url = f"http://192.168.0.1/ubus/?t={int(time.time() * 1000)}"
```

Jika alamat IP pengelolaan router berbeda, sesuaikan endpoint serta header `Referer` dan `Origin` yang terkait agar cocok dengan alamat router. Implementasi saat ini menggunakan endpoint `zte_nwinfo_api` / `nwinfo_get_netinfo milik router.

Aplikasi dirancang untuk antarmuka internal router ZTE tersebut dan **bukan dashboard universal untuk semua jenis router**. Dukungan konfigurasi IP router kustom melalui UI belum termasuk dalam dokumentasi fitur saat ini; perubahan alamat dilakukan melalui konfigurasi kode sumber.

Pengaturan **Frekuensi Update Data** mengubah interval pengambilan data menjadi 1, 2, atau 4 detik.

## Referensi Metrik Sinyal

Dashboard menggunakan ambang batas berikut untuk memberi label kualitas sinyal:

| Metrik | Mantap | Bagus | Cukup | Buruk |
| --- | ---: | ---: | ---: | ---: |
| RSRP | ≥ -80 dBm | -81 hingga -95 dBm | -96 hingga -110 dBm | < -110 dBm |
| RSSI | ≥ -70 dBm | -71 hingga -85 dBm | -86 hingga -100 dBm | < -100 dBm |
| RSRQ | ≥ -10 dB | -11 hingga -15 dB | -16 hingga -20 dB | < -20 dB |
| SINR / SNR | ≥ 20 dB | 10 hingga 19 dB | 0 hingga 9 dB | < 0 dB |

Ambang batas tersebut merupakan acuan bawaan untuk membantu membaca kondisi sinyal secara cepat, bukan jaminan kualitas layanan atau ukuran universal untuk setiap jaringan.

## Pemecahan Masalah

- **Dashboard terus menampilkan “Menghubungkan…” atau data tidak diperbarui**
  - Pastikan komputer/perangkat dapat membuka halaman pengelolaan router.
  - Pastikan alamat IP router di `router_app.py` sudah benar.
  - Periksa apakah endpoint API lokal router dapat diakses.
  - Pada desktop, pastikan bridge pywebview telah siap dan aplikasi tidak diblokir oleh firewall.
- **Nilai sinyal tidak tersedia atau ditampilkan sebagai `-`**
  - Pastikan router terhubung ke jaringan seluler dan respons telemetrinya memuat kolom yang diharapkan.
  - Perubahan firmware dapat mengubah struktur data API router.
- **Ping gagal**
  - Periksa hostname/IP tujuan dan konektivitas jaringan.
  - Beberapa host atau jaringan dapat memblokir ICMP.
- **Speed Test gagal atau mendapat HTTP 429**
  - Server pengujian dapat membatasi permintaan. Coba lagi setelah beberapa saat atau periksa ketersediaan server.
- **Pembaruan tidak menemukan berkas yang cocok**
  - Pastikan rilis menyediakan aset untuk jenis aplikasi yang sedang digunakan (EXE, Python, atau APK).
  - Periksa kanal Stable/Beta dan versi rilis yang dipilih.
- **Updater Windows tidak dapat mengganti aplikasi**
  - Folder instalasi tertentu membutuhkan izin administrator. Setujui permintaan UAC jika muncul.
  - Jika izin ditolak atau proses update gagal, aplikasi seharusnya tetap berjalan dan berkas aplikasi tidak diganti.
- **Tata letak dashboard atau grafik tidak muncul**
  - Periksa koneksi internet karena beberapa pustaka antarmuka dimuat dari CDN eksternal.
- **Ekspor log tidak muncul**
  - Periksa folder tujuan atau gunakan opsi berbagi Android. Tinjau izin penyimpanan yang diminta sistem operasi.

## Keamanan dan Privasi

- Aplikasi berkomunikasi dengan endpoint pengelolaan lokal router menggunakan **HTTP**, bukan HTTPS.
- Implementasi saat ini menonaktifkan peringatan keamanan permintaan urllib3 dan menggunakan verifikasi TLS yang dinonaktifkan pada permintaan router. Hal ini perlu ditinjau kembali jika kode diadaptasi untuk HTTPS.
- Jalankan aplikasi hanya di jaringan lokal yang tepercaya. **Jangan paparkan antarmuka pengelolaan router ke internet publik.**
- Riwayat koneksi disimpan selama sesi aplikasi berjalan dan dapat hilang saat aplikasi dimulai ulang atau ketika riwayat dibersihkan.
- Ekspor diagnostik tidak dirancang untuk menyertakan password, cookie, token, atau kredensial router, tetapi tetap periksa laporan sebelum membagikannya.
- Jangan membagikan tangkapan layar, log, atau berkas konfigurasi yang dapat mengungkap alamat jaringan, identitas perangkat, atau informasi pribadi tanpa memeriksanya terlebih dahulu.

## Pengembangan dan Build

Proyek memiliki implementasi desktop Python/pywebview dan aplikasi Android native berbasis Kotlin.

### Build Windows

Workflow Windows menghasilkan dua jenis paket:
- **Portable EXE** menggunakan PyInstaller.
- **Setup Installer** menggunakan Inno Setup.

### Build Android

APK dibangun melalui Android Gradle. Rilis APK menggunakan signing key yang konsisten agar pembaruan dapat dipasang di atas versi sebelumnya. Keystore dan password signing merupakan rahasia repository dan tidak boleh dimasukkan ke source code.

### Perintah rilis repository

Pemilik repository dapat memicu workflow rilis melalui komentar tersendiri pada Issue atau Pull Request:

- `/cmd` — menampilkan daftar perintah yang tersedia.
- `/build beta` — membangun rilis beta dari branch `dev`.
- `/build stable` — membangun rilis stabil dari branch `main`.

Workflow akan membuat versi rilis, menjalankan build desktop dan Android, lalu menerbitkan GitHub Release. Branch sementara build dibersihkan setelah proses publikasi berhasil. Perintah ini merupakan fitur otomasi maintainer, bukan fitur yang dijalankan dari dalam aplikasi.

## Status Proyek

Proyek ini terutama ditujukan untuk pemantauan pribadi router IRA (Internet Rakyat) ZTE MC8501. Perubahan firmware dapat memengaruhi endpoint internal maupun kolom telemetri yang dikembalikan perangkat. Tidak semua fitur memiliki perilaku identik di desktop dan Android karena sebagian fungsi menggunakan integrasi native masing-masing platform.

Proyek ini dikelola secara independen dan bukan perangkat lunak resmi dari produsen router atau penyedia layanan internet.

## Lisensi dan Penggunaan Ulang

Repositori ini belum menetapkan lisensi perangkat lunak. Sampai lisensi ditambahkan, **jangan menganggap kode atau materi di repositori ini bebas digunakan ulang, dimodifikasi, atau didistribusikan ulang**. Hak atas merek dagang dan aset pihak ketiga tetap berada pada pemilik masing-masing.

---

Jika menemukan masalah atau ingin mengusulkan perubahan, silakan gunakan [Issues](https://github.com/TheKingTermux/ira-zte-live-signal-charts/issues). Harap diingat bahwa repositori ini merupakan proyek independen; kanal tersebut bukan layanan dukungan resmi IRA (Internet Rakyat), PT. Telemedia Komunikasi Pratama, atau ZTE Corporation.
