"""
tests/test_metadata.py – Unit tests for src/metadata.py
"""

from __future__ import annotations

import json
import os

import pytest


SAMPLE_CONFIG = {
    "collection": {
        "name": "Test Collection",
        "description": "A test NFT collection.",
        "symbol": "TST",
        "size": 3,
        "baseUri": "ipfs://TestCID/",
        "royaltyBps": 500,
        "royaltyReceiver": "0x0000000000000000000000000000000000000000",
    },
    "ipfs": {
        "provider": "pinata",
        "gateway": "https://gateway.pinata.cloud/ipfs/",
    },
}

SAMPLE_ATTRIBUTES = [
    {"trait_type": "Background", "value": "Blue"},
    {"trait_type": "Body", "value": "Circle"},
]


# ── build_token_metadata ──────────────────────────────────────────────────────


class TestBuildTokenMetadata:
    def test_basic_fields_present(self):
        from src.metadata import build_token_metadata

        meta = build_token_metadata(1, SAMPLE_ATTRIBUTES, SAMPLE_CONFIG)
        assert meta["name"] == "Test Collection #1"
        assert meta["description"] == "A test NFT collection."
        assert "image" in meta
        assert "attributes" in meta
        assert meta["attributes"] == SAMPLE_ATTRIBUTES

    def test_image_uri_uses_base_uri_when_no_cid(self):
        from src.metadata import build_token_metadata

        meta = build_token_metadata(42, SAMPLE_ATTRIBUTES, SAMPLE_CONFIG)
        assert meta["image"] == "ipfs://TestCID/42.png"

    def test_image_uri_uses_cid_when_provided(self):
        from src.metadata import build_token_metadata

        meta = build_token_metadata(7, SAMPLE_ATTRIBUTES, SAMPLE_CONFIG, image_cid="QmABC")
        assert meta["image"] == "ipfs://QmABC/7.png"
        assert "QmABC" in meta["external_url"]

    def test_token_ids_in_names(self):
        from src.metadata import build_token_metadata

        for token_id in [1, 5, 100]:
            meta = build_token_metadata(token_id, SAMPLE_ATTRIBUTES, SAMPLE_CONFIG)
            assert f"#{token_id}" in meta["name"]


# ── save_token_metadata ───────────────────────────────────────────────────────


class TestSaveTokenMetadata:
    def test_file_created_with_correct_name(self, tmp_path):
        from src.metadata import save_token_metadata, build_token_metadata

        meta = build_token_metadata(3, SAMPLE_ATTRIBUTES, SAMPLE_CONFIG)
        path = save_token_metadata(meta, 3, str(tmp_path))
        assert os.path.isfile(path)
        assert path.endswith("3.json")

    def test_json_is_valid_and_round_trips(self, tmp_path):
        from src.metadata import save_token_metadata, build_token_metadata

        meta = build_token_metadata(1, SAMPLE_ATTRIBUTES, SAMPLE_CONFIG)
        path = save_token_metadata(meta, 1, str(tmp_path))
        with open(path, encoding="utf-8") as fh:
            loaded = json.load(fh)
        assert loaded == meta

    def test_creates_output_dir_if_missing(self, tmp_path):
        from src.metadata import save_token_metadata, build_token_metadata

        meta = build_token_metadata(1, SAMPLE_ATTRIBUTES, SAMPLE_CONFIG)
        new_dir = str(tmp_path / "nested" / "dir")
        path = save_token_metadata(meta, 1, new_dir)
        assert os.path.isfile(path)


# ── generate_collection_metadata ─────────────────────────────────────────────


class TestGenerateCollectionMetadata:
    def test_generates_one_file_per_token(self, tmp_path):
        from src.metadata import generate_collection_metadata

        results = [
            (1, [{"trait_type": "Background", "value": "Blue"}]),
            (2, [{"trait_type": "Background", "value": "Red"}]),
            (3, [{"trait_type": "Background", "value": "Green"}]),
        ]
        paths = generate_collection_metadata(results, SAMPLE_CONFIG, str(tmp_path))
        assert len(paths) == 3
        for path in paths:
            assert os.path.isfile(path)

    def test_metadata_content_is_correct(self, tmp_path):
        from src.metadata import generate_collection_metadata

        results = [(1, SAMPLE_ATTRIBUTES)]
        generate_collection_metadata(results, SAMPLE_CONFIG, str(tmp_path))
        with open(os.path.join(str(tmp_path), "1.json"), encoding="utf-8") as fh:
            meta = json.load(fh)
        assert meta["attributes"] == SAMPLE_ATTRIBUTES


# ── build_collection_summary ──────────────────────────────────────────────────


class TestBuildCollectionSummary:
    def test_summary_counts_traits(self):
        from src.metadata import build_collection_summary

        results = [
            (1, [{"trait_type": "Background", "value": "Blue"}]),
            (2, [{"trait_type": "Background", "value": "Blue"}]),
            (3, [{"trait_type": "Background", "value": "Red"}]),
        ]
        summary = build_collection_summary(results, SAMPLE_CONFIG)
        assert summary["total_supply"] == 3
        bg = summary["traits"]["Background"]
        assert bg["Blue"]["count"] == 2
        assert bg["Red"]["count"] == 1

    def test_summary_percentages_sum_to_100(self):
        from src.metadata import build_collection_summary

        results = [
            (i, [{"trait_type": "Bg", "value": "A" if i % 2 == 0 else "B"}])
            for i in range(1, 11)
        ]
        summary = build_collection_summary(results, SAMPLE_CONFIG)
        bg = summary["traits"]["Bg"]
        total_pct = sum(v["percentage"] for v in bg.values())
        assert abs(total_pct - 100.0) < 0.1

    def test_summary_includes_collection_name(self):
        from src.metadata import build_collection_summary

        summary = build_collection_summary([], SAMPLE_CONFIG)
        assert summary["collection"] == "Test Collection"
