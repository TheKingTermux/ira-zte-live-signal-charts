#!/usr/bin/env python3
"""Generate Windows and Android application icons from the repository's source artwork."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ICON = ROOT / "build-assets" / "icons" / "ira-zte-icon.png"


def load_source_icon() -> Image.Image:
    """Load the checked-in artwork and normalize it to a square RGBA image."""
    if not SOURCE_ICON.is_file():
        raise FileNotFoundError(
            f"Source icon not found: {SOURCE_ICON}. "
            "Add build-assets/icons/ira-zte-icon.png to the branch before building."
        )

    with Image.open(SOURCE_ICON) as source:
        image = source.convert("RGBA")
    # Keep the full artwork visible, even if a replacement source is not square.
    side = max(image.width, image.height)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.alpha_composite(image, ((side - image.width) // 2, (side - image.height) // 2))
    return square


def resize_icon(source: Image.Image, size: int) -> Image.Image:
    return ImageOps.contain(source, (size, size), method=Image.Resampling.LANCZOS)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate embedded application icons from ira-zte-icon.png."
    )
    parser.add_argument(
        "--platform", choices=("windows", "android", "all"), default="all"
    )
    args = parser.parse_args()
    source = load_source_icon()

    if args.platform in ("windows", "all"):
        output = ROOT / "build-assets" / "icons" / "IRA_ZTE_Live_Signal_Charts.ico"
        output.parent.mkdir(parents=True, exist_ok=True)
        resize_icon(source, 256).save(
            output,
            format="ICO",
            sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
        )
        print(f"Generated {output}")

    if args.platform in ("android", "all"):
        resources = ROOT / "android" / "app" / "src" / "main" / "res"
        densities = (
            ("mipmap-mdpi", 48),
            ("mipmap-hdpi", 72),
            ("mipmap-xhdpi", 96),
            ("mipmap-xxhdpi", 144),
            ("mipmap-xxxhdpi", 192),
        )
        for folder, size in densities:
            target = resources / folder / "ic_launcher.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            resize_icon(source, size).save(target, format="PNG", optimize=True)
            print(f"Generated {target}")


if __name__ == "__main__":
    main()
