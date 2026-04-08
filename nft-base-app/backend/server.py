"""
server.py – FastAPI backend for the NFT Generator dapp.

Endpoints
---------
GET  /api/collection  → collection metadata from config.json
POST /api/generate    → generate one unique NFT, upload to IPFS, return token URI

Run
---
    cd nft-base-app/backend
    pip install -r requirements.txt
    uvicorn server:app --reload --port 8000

Environment variables (same as root .env.example)
---------------------------------------------------
    PINATA_JWT   or   PINATA_API_KEY + PINATA_API_SECRET
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ── Python path setup ─────────────────────────────────────────────────────────
# Add the generator package root so `from src.xxx import` works.
GENERATOR_DIR = Path(__file__).parent / "generator"
sys.path.insert(0, str(GENERATOR_DIR))

from src.generator import load_config_layers, generate_single  # noqa: E402
from src.ipfs import PinataClient, IPFSUploadError              # noqa: E402

# ── Config ────────────────────────────────────────────────────────────────────
CONFIG_PATH = GENERATOR_DIR / "config.json"
LAYERS_DIR  = GENERATOR_DIR / "layers"

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="NFT Generator API", version="1.0.0")

# ── CORS ──────────────────────────────────────────────────────────────────────
# Default to localhost only.  Override via CORS_ORIGINS env var for production.
# Example: CORS_ORIGINS="https://your-dapp.com,https://www.your-dapp.com"
_cors_origins_env = os.environ.get("CORS_ORIGINS", "")
_allowed_origins = (
    [o.strip() for o in _cors_origins_env.split(",") if o.strip()]
    if _cors_origins_env
    else ["http://localhost:3000", "http://127.0.0.1:3000"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


def _load_config() -> dict:
    if not CONFIG_PATH.is_file():
        raise HTTPException(
            status_code=500,
            detail=f"config.json not found at {CONFIG_PATH}",
        )
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/api/collection")
def get_collection() -> dict:
    """Return collection metadata from config.json."""
    config = _load_config()
    col = config["collection"]
    return {
        "name":        col["name"],
        "description": col["description"],
        "symbol":      col["symbol"],
        "size":        col["size"],
        "baseUri":     col.get("baseUri", ""),
        "royaltyBps":  col.get("royaltyBps", 0),
    }


@app.post("/api/generate")
def generate_nft() -> dict:
    """
    Generate one unique NFT trait combination, composite the image,
    upload image and metadata to IPFS via Pinata, and return the token URI.

    Returns
    -------
    {
        "tokenURI":   "ipfs://<metadata-cid>",
        "imageUrl":   "https://gateway.pinata.cloud/ipfs/<image-cid>",
        "attributes": [{"trait_type": "...", "value": "..."}, ...],
        "metadata":   { ... }
    }
    """
    config = _load_config()

    if not LAYERS_DIR.is_dir():
        raise HTTPException(
            status_code=500,
            detail=f"Layers directory not found: {LAYERS_DIR}",
        )

    # Generate one NFT image + attributes
    try:
        layers = load_config_layers(config, str(LAYERS_DIR))
        width  = config["image"]["width"]
        height = config["image"]["height"]
        image, attributes = generate_single(layers, width, height)
    except (FileNotFoundError, RuntimeError) as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    # Save image to a temp file
    tmp_dir = tempfile.mkdtemp(prefix="nft_gen_")
    token_slug = uuid.uuid4().hex[:12]
    image_path = os.path.join(tmp_dir, f"{token_slug}.png")
    image.save(image_path, format="PNG")

    # Upload image to IPFS
    try:
        client = PinataClient()
    except EnvironmentError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    try:
        image_cid = client.pin_file(
            image_path,
            name=f"{config['collection']['name']}-image-{token_slug}",
        )
    except IPFSUploadError as exc:
        raise HTTPException(status_code=502, detail=f"IPFS image upload failed: {exc}")
    finally:
        # Clean up temp file
        try:
            os.remove(image_path)
            os.rmdir(tmp_dir)
        except OSError:
            pass

    col = config["collection"]
    ipfs_gateway = config.get("ipfs", {}).get(
        "gateway", "https://gateway.pinata.cloud/ipfs/"
    )

    # Build ERC-721 metadata
    metadata = {
        "name":        f"{col['name']} – {token_slug}",
        "description": col["description"],
        "image":       f"ipfs://{image_cid}",
        "attributes":  attributes,
    }

    # Upload metadata JSON to IPFS
    try:
        metadata_cid = client.pin_json(
            metadata,
            name=f"{col['name']}-metadata-{token_slug}",
        )
    except IPFSUploadError as exc:
        raise HTTPException(
            status_code=502, detail=f"IPFS metadata upload failed: {exc}"
        )

    token_uri  = f"ipfs://{metadata_cid}"
    image_url  = f"{ipfs_gateway.rstrip('/')}/{image_cid}"

    return {
        "tokenURI":   token_uri,
        "imageUrl":   image_url,
        "attributes": attributes,
        "metadata":   metadata,
    }
