"""
generator.py – Layer-based NFT image generator.

Reads layer folders defined in config, randomly selects traits according
to their weights, composites them into a final PNG image, and returns the
ordered list of chosen traits for metadata generation.
"""

from __future__ import annotations

import os
import random
from pathlib import Path
from typing import Any

from PIL import Image


def load_config_layers(config: dict[str, Any], layers_dir: str) -> list[dict[str, Any]]:
    """Validate that all required trait image files exist and return layer specs."""
    validated: list[dict[str, Any]] = []
    layers_path = Path(layers_dir)

    for layer in config["layers"]:
        layer_folder = layers_path / layer["name"]
        if not layer_folder.is_dir():
            raise FileNotFoundError(
                f"Layer folder not found: {layer_folder}. "
                f"Create the folder and add trait PNG files."
            )
        traits_with_paths: list[dict[str, Any]] = []
        for trait in layer["traits"]:
            trait_path = layer_folder / trait["file"]
            if not trait_path.is_file():
                raise FileNotFoundError(
                    f"Trait file not found: {trait_path}."
                )
            traits_with_paths.append({**trait, "path": str(trait_path)})
        validated.append({**layer, "traits": traits_with_paths})

    return validated


def pick_trait(layer: dict[str, Any]) -> dict[str, Any] | None:
    """
    Randomly select a trait from *layer* respecting weights.

    For optional layers a ``noneWeight`` key may be present.  When "None" is
    selected the function returns *None* (the layer is skipped).
    """
    traits = layer["traits"]
    weights = [t["weight"] for t in traits]

    none_weight = layer.get("noneWeight", 0)
    if none_weight > 0:
        # Add a sentinel "None" option
        traits = list(traits) + [{"name": "None", "weight": none_weight, "path": None}]
        weights = weights + [none_weight]

    chosen = random.choices(traits, weights=weights, k=1)[0]
    if chosen["path"] is None:
        return None
    return chosen


def composite_image(
    chosen_traits: list[dict[str, Any]],
    width: int,
    height: int,
) -> Image.Image:
    """Composite layer images in order to produce the final NFT image."""
    canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for trait in chosen_traits:
        layer_img = Image.open(trait["path"]).convert("RGBA")
        layer_img = layer_img.resize((width, height), Image.LANCZOS)
        canvas = Image.alpha_composite(canvas, layer_img)
    return canvas.convert("RGB")


def generate_single(
    layers: list[dict[str, Any]],
    width: int,
    height: int,
) -> tuple[Image.Image, list[dict[str, str]]]:
    """
    Generate one NFT image.

    Returns the composed PIL image and the list of selected trait dicts
    ``[{"trait_type": ..., "value": ...}, ...]``.
    """
    chosen_traits: list[dict[str, Any]] = []
    selected_attributes: list[dict[str, str]] = []

    for layer in layers:
        trait = pick_trait(layer)
        if trait is not None:
            chosen_traits.append(trait)
            selected_attributes.append(
                {"trait_type": layer["name"], "value": trait["name"]}
            )

    image = composite_image(chosen_traits, width, height)
    return image, selected_attributes


def is_duplicate(
    attributes: list[dict[str, str]],
    existing: list[list[dict[str, str]]],
) -> bool:
    """Return True if *attributes* already appears in *existing*."""
    return attributes in existing


def generate_collection(
    config: dict[str, Any],
    layers_dir: str,
    output_images_dir: str,
) -> list[tuple[int, list[dict[str, str]]]]:
    """
    Generate the full NFT collection.

    Saves PNG images to *output_images_dir* and returns a list of
    ``(token_id, attributes)`` pairs for metadata generation.
    """
    layers = load_config_layers(config, layers_dir)
    cfg_image = config["image"]
    width: int = cfg_image["width"]
    height: int = cfg_image["height"]
    collection_size: int = config["collection"]["size"]

    os.makedirs(output_images_dir, exist_ok=True)

    results: list[tuple[int, list[dict[str, str]]]] = []
    generated_attrs: list[list[dict[str, str]]] = []
    attempts = 0
    max_attempts = collection_size * 10

    token_id = 1
    while len(results) < collection_size:
        if attempts >= max_attempts:
            raise RuntimeError(
                f"Could not generate {collection_size} unique NFTs after "
                f"{max_attempts} attempts. Reduce collection size or add more traits."
            )
        attempts += 1

        image, attributes = generate_single(layers, width, height)

        if is_duplicate(attributes, generated_attrs):
            continue

        generated_attrs.append(attributes)
        image_path = os.path.join(output_images_dir, f"{token_id}.png")
        image.save(image_path, format="PNG")
        results.append((token_id, attributes))
        token_id += 1

    return results
