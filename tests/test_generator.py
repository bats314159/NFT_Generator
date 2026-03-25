"""
tests/test_generator.py – Unit tests for src/generator.py
"""

from __future__ import annotations

import os
import random
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

# ── Helpers ───────────────────────────────────────────────────────────────────


def make_png(path: str, size: tuple[int, int] = (64, 64), colour: tuple = (255, 0, 0, 128)) -> None:
    """Create a small RGBA PNG at *path* for testing."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img = Image.new("RGBA", size, colour)
    img.save(path, format="PNG")


def build_layer_dir(base: Path, layers_spec: list[dict]) -> None:
    """Populate *base/layers/* with dummy PNGs matching *layers_spec*."""
    for layer in layers_spec:
        folder = base / "layers" / layer["name"]
        folder.mkdir(parents=True, exist_ok=True)
        for trait in layer["traits"]:
            make_png(str(folder / trait["file"]))


SIMPLE_CONFIG = {
    "collection": {
        "name": "Test NFT",
        "description": "A test collection.",
        "symbol": "TST",
        # 3 × 3 = 9 unique combos; we only request 4 to leave headroom
        "size": 4,
        "baseUri": "ipfs://test/",
        "royaltyBps": 500,
        "royaltyReceiver": "0x0000000000000000000000000000000000000000",
    },
    "image": {"width": 64, "height": 64, "format": "PNG"},
    "layers": [
        {
            "name": "Background",
            "required": True,
            "traits": [
                {"name": "Blue",   "weight": 40, "file": "blue.png"},
                {"name": "Red",    "weight": 30, "file": "red.png"},
                {"name": "Green",  "weight": 30, "file": "green.png"},
            ],
        },
        {
            "name": "Body",
            "required": True,
            "traits": [
                {"name": "Circle",   "weight": 40, "file": "circle.png"},
                {"name": "Square",   "weight": 30, "file": "square.png"},
                {"name": "Triangle", "weight": 30, "file": "triangle.png"},
            ],
        },
    ],
    "network": {"name": "base", "chainId": 8453},
    "ipfs": {"provider": "pinata", "gateway": "https://gateway.pinata.cloud/ipfs/"},
}


# ── load_config_layers ────────────────────────────────────────────────────────


class TestLoadConfigLayers:
    def test_returns_validated_layers(self, tmp_path):
        build_layer_dir(tmp_path, SIMPLE_CONFIG["layers"])
        from src.generator import load_config_layers

        layers = load_config_layers(SIMPLE_CONFIG, str(tmp_path / "layers"))
        assert len(layers) == 2
        for layer in layers:
            for trait in layer["traits"]:
                assert "path" in trait
                assert os.path.isfile(trait["path"])

    def test_missing_layer_folder_raises(self, tmp_path):
        from src.generator import load_config_layers

        with pytest.raises(FileNotFoundError, match="Layer folder not found"):
            load_config_layers(SIMPLE_CONFIG, str(tmp_path / "layers"))

    def test_missing_trait_file_raises(self, tmp_path):
        from src.generator import load_config_layers

        # Create layer folder but not the trait file
        (tmp_path / "layers" / "Background").mkdir(parents=True)
        (tmp_path / "layers" / "Body").mkdir(parents=True)
        # Only create some files
        make_png(str(tmp_path / "layers" / "Background" / "blue.png"))
        # red.png is missing – should raise

        with pytest.raises(FileNotFoundError, match="Trait file not found"):
            load_config_layers(SIMPLE_CONFIG, str(tmp_path / "layers"))


# ── pick_trait ────────────────────────────────────────────────────────────────


class TestPickTrait:
    def test_always_picks_from_required_layer(self):
        from src.generator import pick_trait

        layer = {
            "name": "Background",
            "required": True,
            "traits": [
                {"name": "Blue", "weight": 100, "file": "blue.png", "path": "/fake/blue.png"},
            ],
        }
        result = pick_trait(layer)
        assert result is not None
        assert result["name"] == "Blue"

    def test_none_returned_when_none_weight_selected(self):
        """With 100% none weight the layer should always be skipped."""
        from src.generator import pick_trait

        layer = {
            "name": "Accessory",
            "required": False,
            "noneWeight": 1000,
            "traits": [
                {"name": "Hat", "weight": 1, "file": "hat.png", "path": "/fake/hat.png"},
            ],
        }
        # Run many times – with weight 1 vs 1000 at least some calls should be None
        results = [pick_trait(layer) for _ in range(50)]
        assert any(r is None for r in results)

    def test_weights_respected(self):
        """A 100-weight trait should almost always be chosen over a 1-weight trait."""
        from src.generator import pick_trait

        layer = {
            "name": "Body",
            "required": True,
            "traits": [
                {"name": "Common", "weight": 999, "file": "c.png", "path": "/fake/c.png"},
                {"name": "Rare",   "weight": 1,   "file": "r.png", "path": "/fake/r.png"},
            ],
        }
        random.seed(0)
        results = [pick_trait(layer)["name"] for _ in range(200)]
        assert results.count("Common") > results.count("Rare")


# ── composite_image ───────────────────────────────────────────────────────────


class TestCompositeImage:
    def test_output_size(self, tmp_path):
        from src.generator import composite_image

        p1 = str(tmp_path / "layer1.png")
        p2 = str(tmp_path / "layer2.png")
        make_png(p1, (32, 32), (255, 0, 0, 200))
        make_png(p2, (32, 32), (0, 0, 255, 100))

        traits = [{"path": p1}, {"path": p2}]
        img = composite_image(traits, 64, 64)
        assert img.size == (64, 64)
        assert img.mode == "RGB"

    def test_single_layer(self, tmp_path):
        from src.generator import composite_image

        p = str(tmp_path / "only.png")
        make_png(p, (64, 64), (200, 100, 50, 255))
        img = composite_image([{"path": p}], 64, 64)
        assert img.size == (64, 64)


# ── generate_collection ───────────────────────────────────────────────────────


class TestGenerateCollection:
    def test_generates_correct_count(self, tmp_path):
        from src.generator import generate_collection

        build_layer_dir(tmp_path, SIMPLE_CONFIG["layers"])
        results = generate_collection(
            SIMPLE_CONFIG,
            str(tmp_path / "layers"),
            str(tmp_path / "output" / "images"),
        )
        assert len(results) == SIMPLE_CONFIG["collection"]["size"]

    def test_images_are_saved(self, tmp_path):
        from src.generator import generate_collection

        build_layer_dir(tmp_path, SIMPLE_CONFIG["layers"])
        images_dir = str(tmp_path / "output" / "images")
        generate_collection(SIMPLE_CONFIG, str(tmp_path / "layers"), images_dir)

        for i in range(1, SIMPLE_CONFIG["collection"]["size"] + 1):
            assert os.path.isfile(os.path.join(images_dir, f"{i}.png"))

    def test_no_duplicate_attribute_sets(self, tmp_path):
        from src.generator import generate_collection

        build_layer_dir(tmp_path, SIMPLE_CONFIG["layers"])
        results = generate_collection(
            SIMPLE_CONFIG,
            str(tmp_path / "layers"),
            str(tmp_path / "output" / "images"),
        )
        attr_sets = [tuple(sorted((a["trait_type"], a["value"]) for a in attrs))
                     for _, attrs in results]
        assert len(attr_sets) == len(set(attr_sets))

    def test_raises_when_uniqueness_impossible(self, tmp_path):
        """Collection of 5 with only 2 possible combos should raise RuntimeError."""
        from src.generator import generate_collection

        config = {
            **SIMPLE_CONFIG,
            "collection": {**SIMPLE_CONFIG["collection"], "size": 5},
            "layers": [
                {
                    "name": "Background",
                    "required": True,
                    "traits": [
                        {"name": "A", "weight": 1, "file": "a.png"},
                    ],
                },
                {
                    "name": "Body",
                    "required": True,
                    "traits": [
                        {"name": "X", "weight": 1, "file": "x.png"},
                    ],
                },
            ],
        }
        build_layer_dir(tmp_path, config["layers"])
        with pytest.raises(RuntimeError, match="unique NFTs"):
            generate_collection(config, str(tmp_path / "layers"), str(tmp_path / "images"))
