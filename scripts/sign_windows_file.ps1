<#
  Menandatangani satu berkas (EXE portabel atau installer) dengan sertifikat tetap dari secret repositori,
  lalu memastikan tanda tangannya memang memakai sertifikat yang diharapkan.
  Dipanggil oleh .github/workflows/build-exe.yml setelah langkah "Prepare persistent Windows signing certificate".

  Variabel lingkungan yang dibutuhkan: SIGNTOOL_PATH, WINDOWS_CERT_PATH, WINDOWS_CERT_PASSWORD, WINDOWS_CERT_THUMBPRINT
#>
param(
    [Parameter(Mandatory = $true)][string]$File
)

$ErrorActionPreference = "Stop"

foreach ($name in "SIGNTOOL_PATH", "WINDOWS_CERT_PATH", "WINDOWS_CERT_PASSWORD", "WINDOWS_CERT_THUMBPRINT") {
    if ([string]::IsNullOrEmpty([Environment]::GetEnvironmentVariable($name))) {
        throw "Variabel lingkungan $name belum diset (jalankan langkah persiapan sertifikat lebih dulu)."
    }
}
if (!(Test-Path -LiteralPath $File)) { throw "Berkas tidak ditemukan: $File" }

# Beberapa server timestamp sebagai cadangan; stempel waktu menjaga tanda tangan tetap valid setelah sertifikat kedaluwarsa.
$servers = @(
    "http://timestamp.digicert.com",
    "http://timestamp.sectigo.com",
    "http://timestamp.globalsign.com/tsa/r6advanced1"
)
$signed = $false
foreach ($server in $servers) {
    & $env:SIGNTOOL_PATH sign /f $env:WINDOWS_CERT_PATH /p $env:WINDOWS_CERT_PASSWORD /fd SHA256 /tr $server /td SHA256 /d "IRA ZTE Live Signal Charts" $File
    if ($LASTEXITCODE -eq 0) { $signed = $true; break }
    Write-Warning "Penandatanganan dengan timestamp $server gagal (kode $LASTEXITCODE); mencoba server lain."
}
if (-not $signed) { throw "Gagal menandatangani $File." }

# Sertifikat self-signed tidak dipercaya sistem (status bukan 'Valid'), jadi yang diperiksa adalah thumbprint penanda tangan.
$signature = Get-AuthenticodeSignature -LiteralPath $File
if (-not $signature.SignerCertificate -or $signature.SignerCertificate.Thumbprint -ne $env:WINDOWS_CERT_THUMBPRINT) {
    throw "Tanda tangan pada $File tidak sesuai dengan sertifikat yang diharapkan."
}
Write-Host "Ditandatangani: $File (thumbprint $($signature.SignerCertificate.Thumbprint))"
