"""
utils.py – Shared utility helpers for the NFT Generator.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any


def load_config(config_path: str = "config.json") -> dict[str, Any]:
    """Load and return the JSON config from *config_path*."""
    path = Path(config_path)
    if not path.is_file():
        raise FileNotFoundError(
            f"Config file not found: {config_path}. "
            "Copy config.json.example to config.json and customise it."
        )
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def ensure_output_dirs(base_dir: str = "output") -> tuple[str, str]:
    """Create output/images and output/metadata directories if needed."""
    images_dir = os.path.join(base_dir, "images")
    metadata_dir = os.path.join(base_dir, "metadata")
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(metadata_dir, exist_ok=True)
    return images_dir, metadata_dir


def sha256_file(path: str) -> str:
    """Return the hex SHA-256 digest of the file at *path*."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(data: Any, path: str) -> None:
    """Serialise *data* to *path* with 2-space indent."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def print_step(msg: str) -> None:
    """Print a formatted progress step to stdout."""
    print(f"\n{'='*60}\n  {msg}\n{'='*60}", flush=True)


def print_ok(msg: str) -> None:
    print(f"  ✓ {msg}", flush=True)


def print_err(msg: str) -> None:
    print(f"  ✗ {msg}", file=sys.stderr, flush=True)


def project_root() -> Path:
    """Return the repository root directory (parent of *src/*)."""
    return Path(__file__).parent.parent
