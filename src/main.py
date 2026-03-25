"""
main.py – CLI entry point for the NFT Generator.

Usage
-----
Generate a collection (images + metadata):

    python -m src.main generate \\
        --config config.json \\
        --layers layers/ \\
        --output output/

Upload to IPFS (requires Pinata credentials in env):

    python -m src.main upload \\
        --config config.json \\
        --output output/

Generate and upload in one step:

    python -m src.main run \\
        --config config.json \\
        --layers layers/ \\
        --output output/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.generator import generate_collection
from src.metadata import generate_collection_metadata, build_collection_summary
from src.utils import (
    load_config,
    ensure_output_dirs,
    write_json,
    print_step,
    print_ok,
    print_err,
    project_root,
)


def cmd_generate(args: argparse.Namespace) -> int:
    """Generate images and metadata without uploading."""
    try:
        config = load_config(args.config)
    except FileNotFoundError as exc:
        print_err(str(exc))
        return 1

    images_dir, metadata_dir = ensure_output_dirs(args.output)

    print_step(
        f"Generating {config['collection']['size']} NFTs "
        f"for '{config['collection']['name']}'"
    )

    try:
        results = generate_collection(config, args.layers, images_dir)
    except (FileNotFoundError, RuntimeError) as exc:
        print_err(str(exc))
        return 1

    print_ok(f"Images saved to: {images_dir}")

    print_step("Generating metadata JSON files")
    paths = generate_collection_metadata(results, config, metadata_dir)
    print_ok(f"Metadata saved to: {metadata_dir}  ({len(paths)} files)")

    summary = build_collection_summary(results, config)
    summary_path = str(Path(args.output) / "summary.json")
    write_json(summary, summary_path)
    print_ok(f"Rarity summary:   {summary_path}")

    return 0


def cmd_upload(args: argparse.Namespace) -> int:
    """Upload previously generated output to IPFS via Pinata."""
    # Import here so missing env vars only raise during upload
    try:
        from src.ipfs import PinataClient, IPFSUploadError
    except ImportError as exc:
        print_err(f"Could not import IPFS module: {exc}")
        return 1

    try:
        config = load_config(args.config)
    except FileNotFoundError as exc:
        print_err(str(exc))
        return 1

    images_dir, metadata_dir = ensure_output_dirs(args.output)

    try:
        client = PinataClient()
    except EnvironmentError as exc:
        print_err(str(exc))
        return 1

    print_step("Uploading images to IPFS")
    try:
        images_cid, metadata_cid = client.upload_images_and_metadata(
            images_dir,
            metadata_dir,
            collection_name=config["collection"]["name"],
        )
    except (IPFSUploadError, FileNotFoundError) as exc:
        print_err(str(exc))
        return 1

    print_ok(f"Images CID:   ipfs://{images_cid}")
    print_ok(f"Metadata CID: ipfs://{metadata_cid}")

    # Persist CIDs so the user can update their smart contract
    cids_path = str(Path(args.output) / "cids.json")
    write_json({"imagesCid": images_cid, "metadataCid": metadata_cid}, cids_path)
    print_ok(f"CIDs saved to: {cids_path}")
    print_ok(
        f"Set baseURI in your contract to: ipfs://{metadata_cid}/"
    )

    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """Generate images + metadata, then upload to IPFS."""
    rc = cmd_generate(args)
    if rc != 0:
        return rc
    return cmd_upload(args)


def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="nft-generator",
        description="Generate and deploy NFT collections.",
    )
    sub = root.add_subparsers(dest="command", required=True)

    # ── generate ──────────────────────────────────────────────────────
    gen = sub.add_parser("generate", help="Generate NFT images and metadata.")
    gen.add_argument("--config", default="config.json", help="Path to config.json")
    gen.add_argument(
        "--layers", default="layers", help="Directory containing layer folders"
    )
    gen.add_argument("--output", default="output", help="Output base directory")

    # ── upload ────────────────────────────────────────────────────────
    upl = sub.add_parser("upload", help="Upload output folder to IPFS via Pinata.")
    upl.add_argument("--config", default="config.json", help="Path to config.json")
    upl.add_argument("--output", default="output", help="Output base directory")

    # ── run (generate + upload) ───────────────────────────────────────
    run = sub.add_parser("run", help="Generate and upload in one step.")
    run.add_argument("--config", default="config.json", help="Path to config.json")
    run.add_argument(
        "--layers", default="layers", help="Directory containing layer folders"
    )
    run.add_argument("--output", default="output", help="Output base directory")

    return root


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    dispatch = {
        "generate": cmd_generate,
        "upload": cmd_upload,
        "run": cmd_run,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
