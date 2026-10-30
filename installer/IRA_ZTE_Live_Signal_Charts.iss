#ifndef MyAppVersion
  #define MyAppVersion "dev"
#endif

#define MyAppName "IRA ZTE Live Signal Charts"
#define MyAppExeName "IRA_ZTE_Live_Signal_Charts.exe"

[Setup]
AppId={{7F3E5E91-8D15-4B7C-AE61-1A2B3C4D5E6F}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
; Judul tanpa nomor versi: tanpa AppVerName, Inno Setup memakai "{AppName} version {AppVersion}"
; sebagai nama di Aplikasi Terpasang/Uninstall. Nomor versi tetap tampil di kolom Versi (AppVersion).
AppVerName={#MyAppName}
UninstallDisplayName={#MyAppName}
AppPublisher=TheKingTermux
; Pasang per-pengguna (tanpa admin) agar updater di dalam aplikasi bisa
; menimpa EXE sendiri. Folder Program Files butuh hak admin sehingga
; pembaruan otomatis gagal di sana.
PrivilegesRequired=lowest
DefaultDirName={autopf}\IRA ZTE Live Signal Charts
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
OutputDir=..\dist
OutputBaseFilename=IRA_ZTE_Live_Signal_Charts-Setup-{#MyAppVersion}
SetupIconFile=..\build-assets\icons\IRA_ZTE_Live_Signal_Charts.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked
Name: "startup"; Description: "Jalankan {#MyAppName} saat &Windows dimulai"; GroupDescription: "Opsi tambahan:"; Flags: unchecked

[Files]
Source: "..\dist\IRA_ZTE_Live_Signal_Charts-Portable-{#MyAppVersion}.exe"; DestDir: "{app}"; DestName: "{#MyAppExeName}"; Flags: ignoreversion

[Registry]
; Jalankan saat Windows dimulai (per-pengguna). Opsi ini juga bisa diubah dari Pengaturan di dalam aplikasi.
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "{#MyAppName}"; ValueData: """{app}\{#MyAppExeName}"""; Flags: uninsdeletevalue; Tasks: startup

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: postinstall nowait skipifsilent

[Code]
// Hapus entri startup saat uninstall, termasuk jika diaktifkan belakangan dari Pengaturan aplikasi
// (bukan lewat opsi installer), agar tidak tersisa entri yang menunjuk ke file yang sudah dihapus.
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
    RegDeleteValue(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Run', '{#MyAppName}');
end;
