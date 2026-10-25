#!/usr/bin/env python3
"""Generate matching embedded application icons for Windows EXE and Android APK."""
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
BG = (16, 24, 39)
BLUE = (56, 189, 248)
PURPLE = (129, 140, 248)
GREEN = (74, 222, 128)
CYAN = (34, 211, 238)


def lerp(a: tuple[int, int, int], b: tuple[int, int, int], t: float):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def make_icon(size: int, android: bool = False) -> Image.Image:
    accent_a, accent_b = (GREEN, CYAN) if android else (BLUE, PURPLE)
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    # Rounded dark tile, with a diagonal accent gradient.
    pad = max(1, round(size * 0.025))
    tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pixels = tile.load()
    for y in range(size):
        for x in range(size):
            t = (x + y) / max(1, 2 * (size - 1))
            c = lerp(BG, lerp(accent_a, accent_b, t) if t > 0.72 else BG, 1.0)
            pixels[x, y] = (*c, 255)
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle((pad, pad, size-pad-1, size-pad-1), radius=round(size*0.22), fill=255)
    tile.putalpha(mask)
    image.alpha_composite(tile)
    draw = ImageDraw.Draw(image)
    # Signal bars and a rising signal trace.
    white = (245, 250, 255, 255)
    x0, y0 = size * 0.22, size * 0.70
    bar_w = size * 0.105
    gap = size * 0.055
    heights = [0.20, 0.32, 0.45, 0.60]
    for i, h in enumerate(heights):
        x = x0 + i * (bar_w + gap)
        draw.rounded_rectangle((int(x), int(y0-size*h), int(x+bar_w), int(y0)), radius=max(1, round(size*0.025)), fill=white)
    points = [
        (size*0.20, size*0.43), (size*0.38, size*0.34),
        (size*0.53, size*0.45), (size*0.70, size*0.25),
        (size*0.82, size*0.31),
    ]
    draw.line(points, fill=(*accent_a, 255), width=max(2, round(size*0.055)), joint="curve")
    r = max(2, round(size*0.045))
    for x, y in points:
        draw.ellipse((int(x-r), int(y-r), int(x+r), int(y+r)), fill=white)
    return image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", choices=("windows", "android", "all"), default="all")
    args = parser.parse_args()
    if args.platform in ("windows", "all"):
        out = ROOT / "build-assets" / "IRA_ZTE_Live_Signal_Charts.ico"
        out.parent.mkdir(parents=True, exist_ok=True)
        icon = make_icon(256)
        icon.save(out, format="ICO", sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
        print(f"Generated {out}")
    if args.platform in ("android", "all"):
        res = ROOT / "android" / "app" / "src" / "main" / "res"
        for folder, size in (("mipmap-mdpi",48),("mipmap-hdpi",72),("mipmap-xhdpi",96),("mipmap-xxhdpi",144),("mipmap-xxxhdpi",192)):
            target = res / folder / "ic_launcher.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            make_icon(size, android=True).save(target, format="PNG", optimize=True)
            print(f"Generated {target}")


if __name__ == "__main__":
    main()
