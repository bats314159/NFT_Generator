"""
metadata.py – ERC-721 compatible JSON metadata generation.

Generates per-token metadata JSON files according to the OpenSea metadata
standard (https://docs.opensea.io/docs/metadata-standards).
"""

from __future__ import annotations

import json
import os
from typing import Any


def build_token_metadata(
    token_id: int,
    attributes: list[dict[str, str]],
    config: dict[str, Any],
    image_cid: str | None = None,
) -> dict[str, Any]:
    """
    Build a single token's metadata dict.

    Parameters
    ----------
    token_id:
        1-based token identifier.
    attributes:
        List of ``{"trait_type": ..., "value": ...}`` dicts.
    config:
        Top-level config dict (used for collection name / description).
    image_cid:
        Optional IPFS CID for the image.  When provided the ``image`` field
        is set to ``ipfs://<cid>/<token_id>.png``.  Otherwise the image URI
        is left as a placeholder.
    """
    collection = config["collection"]
    base_uri = collection.get("baseUri", "ipfs://REPLACE_WITH_METADATA_CID/")
    ipfs_cfg = config.get("ipfs", {})
    gateway = ipfs_cfg.get("gateway", "https://gateway.pinata.cloud/ipfs/")

    if image_cid:
        image_uri = f"ipfs://{image_cid}/{token_id}.png"
        external_url = f"{gateway.rstrip('/')}/{image_cid}/{token_id}.png"
    else:
        image_uri = f"{base_uri}{token_id}.png"
        external_url = f"{base_uri}{token_id}.png"

    return {
        "name": f"{collection['name']} #{token_id}",
        "description": collection["description"],
        "image": image_uri,
        "external_url": external_url,
        "attributes": attributes,
    }


def save_token_metadata(
    metadata: dict[str, Any],
    token_id: int,
    output_dir: str,
) -> str:
    """Serialise *metadata* to ``<output_dir>/<token_id>.json`` and return the path."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{token_id}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(metadata, fh, indent=2)
    return path


def generate_collection_metadata(
    results: list[tuple[int, list[dict[str, str]]]],
    config: dict[str, Any],
    output_metadata_dir: str,
    image_cid: str | None = None,
) -> list[str]:
    """
    Generate and save metadata JSON for every token in *results*.

    Returns a list of file paths for the saved JSON files.
    """
    saved_paths: list[str] = []
    for token_id, attributes in results:
        metadata = build_token_metadata(token_id, attributes, config, image_cid)
        path = save_token_metadata(metadata, token_id, output_metadata_dir)
        saved_paths.append(path)
    return saved_paths


def build_collection_summary(
    results: list[tuple[int, list[dict[str, str]]]],
    config: dict[str, Any],
) -> dict[str, Any]:
    """
    Return a summary dict with trait rarity statistics for the collection.

    Useful for verifying that the generated collection matches expected
    rarity distributions.
    """
    trait_counts: dict[str, dict[str, int]] = {}
    total = len(results)

    for _, attributes in results:
        for attr in attributes:
            trait_type = attr["trait_type"]
            value = attr["value"]
            trait_counts.setdefault(trait_type, {})
            trait_counts[trait_type][value] = trait_counts[trait_type].get(value, 0) + 1

    summary: dict[str, Any] = {
        "collection": config["collection"]["name"],
        "total_supply": total,
        "traits": {},
    }
    for trait_type, counts in trait_counts.items():
        summary["traits"][trait_type] = {
            value: {"count": count, "percentage": round(count / total * 100, 2)}
            for value, count in sorted(counts.items(), key=lambda x: -x[1])
        }
    return summary
