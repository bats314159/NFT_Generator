"""
scripts/create_sample_layers.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Creates minimal placeholder PNG layer images so the generator can be
run immediately without real artwork.  Each image is a solid-colour
square of the configured dimensions.

Usage:
    python scripts/create_sample_layers.py            # uses config.json
    python scripts/create_sample_layers.py --config my_config.json
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Allow running from repo root: python scripts/create_sample_layers.py
sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image, ImageDraw, ImageFont
from src.utils import load_config

# Background colours for each trait category (falls back to grey)
PALETTE = [
    (70, 130, 180),   # steel blue
    (60, 179, 113),   # medium sea green
    (220, 20, 60),    # crimson
    (255, 215, 0),    # gold
    (147, 112, 219),  # medium purple
    (255, 165, 0),    # orange
    (64, 224, 208),   # turquoise
    (255, 105, 180),  # hot pink
]


def make_sample_image(
    width: int,
    height: int,
    bg_colour: tuple[int, int, int],
    label: str,
) -> Image.Image:
    """Return a simple RGBA image with a solid background and a text label."""
    img = Image.new("RGBA", (width, height), (*bg_colour, 200))
    draw = ImageDraw.Draw(img)
    # Draw a subtle border
    draw.rectangle([0, 0, width - 1, height - 1], outline=(255, 255, 255, 180), width=3)
    # Attempt to draw trait name (font may not be available everywhere)
    try:
        draw.text((10, 10), label, fill=(255, 255, 255, 230))
    except Exception:
        pass
    return img


def create_sample_layers(config_path: str) -> None:
    config = load_config(config_path)
    width: int = config["image"]["width"]
    height: int = config["image"]["height"]
    layers_root = Path(config_path).parent / "layers"

    for layer_idx, layer in enumerate(config["layers"]):
        layer_dir = layers_root / layer["name"]
        layer_dir.mkdir(parents=True, exist_ok=True)

        for trait_idx, trait in enumerate(layer["traits"]):
            out_path = layer_dir / trait["file"]
            if out_path.exists():
                print(f"  skip (exists): {out_path}")
                continue
            colour_idx = (layer_idx * 3 + trait_idx) % len(PALETTE)
            img = make_sample_image(width, height, PALETTE[colour_idx], trait["name"])
            img.save(str(out_path), format="PNG")
            print(f"  created: {out_path}")

    print("\nSample layers created in:", layers_root)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create sample placeholder layers.")
    parser.add_argument(
        "--config", default="config.json", help="Path to config.json"
    )
    args = parser.parse_args()
    create_sample_layers(args.config)


if __name__ == "__main__":
    main()
