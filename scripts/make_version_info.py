#!/usr/bin/env python3
"""Buat berkas version-info untuk PyInstaller (--version-file).

Task Manager menampilkan FileDescription pada tab Proses/Aplikasi, bukan nama berkas. Tanpa berkas ini
PyInstaller tidak menulis metadata sehingga yang tampil nama berkas ber-garis-bawah
("IRA_ZTE_Live_Signal_Charts"). Dengan berkas ini yang tampil: "IRA ZTE Live Signal Charts".

Pemakaian:
    python scripts/make_version_info.py --version 1.1-dev.10 --out build-assets/version_info.txt
"""
import argparse
import re
from pathlib import Path

APP_NAME = "IRA ZTE Live Signal Charts"
COMPANY = "TheKingTermux"
EXE_NAME = "IRA_ZTE_Live_Signal_Charts.exe"
COPYRIGHT = "Copyright (c) TheKingTermux"


def parse_version(label):
    """'1.1-dev.10' -> (1, 1, 0, 10); '1.1' -> (1, 1, 0, 0). Tiap bagian dibatasi 0..65535 (aturan Windows)."""
    text = str(label or "").strip()
    text = text[1:] if text[:1] in ("v", "V") else text
    pre = re.search(r"[-.]?(dev|alpha|beta|rc|pre)[.-]?(\d+)?", text, re.IGNORECASE)
    base = text[:pre.start()] if pre else text
    numbers = [int(n) for n in re.findall(r"\d+", base)]
    numbers = (numbers + [0, 0, 0])[:3]
    build = int(pre.group(2)) if pre and pre.group(2) else 0
    return tuple(min(max(n, 0), 65535) for n in (*numbers, build))


def render(label):
    numbers = parse_version(label)
    dotted = ".".join(str(n) for n in numbers)
    tuple_text = ", ".join(str(n) for n in numbers)
    safe_label = str(label or dotted).replace("'", "")
    return f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({tuple_text}),
    prodvers=({tuple_text}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
        StringStruct('CompanyName', '{COMPANY}'),
        StringStruct('FileDescription', '{APP_NAME}'),
        StringStruct('FileVersion', '{dotted}'),
        StringStruct('InternalName', '{APP_NAME}'),
        StringStruct('LegalCopyright', '{COPYRIGHT}'),
        StringStruct('OriginalFilename', '{EXE_NAME}'),
        StringStruct('ProductName', '{APP_NAME}'),
        StringStruct('ProductVersion', '{safe_label}')
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="label versi build, mis. 1.1-dev.10")
    parser.add_argument("--out", required=True, help="berkas keluaran")
    args = parser.parse_args()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(args.version), encoding="utf-8")
    print(f"Menulis {out} (versi {'.'.join(str(n) for n in parse_version(args.version))})")


if __name__ == "__main__":
    main()
