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
; Beri pilihan di awal instalasi: "hanya untuk saya" (default, tanpa admin) atau "semua pengguna" (admin).
; Diperlukan bila folder tujuan di drive lain/Program Files tidak bisa ditulis tanpa hak administrator.
PrivilegesRequiredOverridesAllowed=dialog
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
// Cek apakah folder tujuan bisa dipakai TANPA error "Access is denied" di tengah instalasi.
function IsDirectoryWritable(const Dir: String): Boolean;
var
  Probe: String;
begin
  Probe := AddBackslash(Dir) + 'ira_write_test.tmp';
  Result := SaveStringToFile(Probe, 'ok', False);
  if Result then
    DeleteFile(Probe);
end;

// Folder induk terdekat yang sudah ada (mis. D:\ untuk D:\IRA ZTE yang belum dibuat).
function NearestExistingDir(Dir: String): String;
var
  Parent: String;
  I: Integer;
begin
  Result := RemoveBackslashUnlessRoot(Dir);
  for I := 1 to 32 do
  begin
    if DirExists(Result) then
      Exit;
    Parent := ExtractFileDir(Result);
    if (Parent = '') or (Parent = Result) then
      Break;
    Result := Parent;
  end;
  Result := '';
end;

// Folder yang sudah ada diuji dengan membuat berkas; folder yang belum ada diuji dengan membuat
// sub-folder di induk terdekat (di akar drive biasanya pengguna boleh membuat folder, bukan berkas).
function CanInstallToDir(const Dir: String): Boolean;
var
  Parent, Probe: String;
begin
  if DirExists(Dir) then
  begin
    Result := IsDirectoryWritable(Dir);
    Exit;
  end;
  Parent := NearestExistingDir(Dir);
  if Parent = '' then
  begin
    Result := False;
    Exit;
  end;
  Probe := AddBackslash(Parent) + 'ira_write_test_dir';
  Result := CreateDir(Probe);
  if Result then
    RemoveDir(Probe);
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;
  if CurPageID = wpSelectDir then
  begin
    if not CanInstallToDir(WizardDirValue) then
    begin
      if IsAdminInstallMode then
        MsgBox('Folder tujuan tidak bisa ditulis, bahkan dengan hak administrator.' + #13#10 + #13#10 +
               'Pilih folder lain.', mbError, MB_OK)
      else
        MsgBox('Akses ditolak: folder tujuan memerlukan hak administrator.' + #13#10 + #13#10 +
               'Pilih folder yang bisa Anda tulis (contoh: D:\IRA ZTE), atau jalankan ulang installer ' +
               'dan pilih "Install for all users" agar bisa memasang ke folder tersebut.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

// Hapus entri startup saat uninstall, termasuk jika diaktifkan belakangan dari Pengaturan aplikasi
// (bukan lewat opsi installer), agar tidak tersisa entri yang menunjuk ke file yang sudah dihapus.
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
    RegDeleteValue(HKCU, 'Software\Microsoft\Windows\CurrentVersion\Run', '{#MyAppName}');
end;
