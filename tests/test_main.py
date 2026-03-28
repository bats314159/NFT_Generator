"""
tests/test_main.py - Unit tests for src/main.py CLI commands.

Covers the new ``deploy`` subcommand and the updated ``run`` pipeline.
"""

from __future__ import annotations

import json
import subprocess
from argparse import Namespace
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ── helpers ───────────────────────────────────────────────────────────────────


def _write_cids(output_dir: Path, images_cid: str = "QmImages", metadata_cid: str = "QmMeta") -> Path:
    cids_path = output_dir / "cids.json"
    cids_path.write_text(
        json.dumps({"imagesCid": images_cid, "metadataCid": metadata_cid}),
        encoding="utf-8",
    )
    return cids_path


def _write_config(config_path: Path) -> None:
    config = {
        "collection": {
            "name": "Test",
            "description": "desc",
            "symbol": "TST",
            "size": 1,
            "baseUri": "ipfs://OLD/",
            "contractUri": "",
            "royaltyBps": 500,
            "royaltyReceiver": "0x0000000000000000000000000000000000000000",
        },
        "image": {"width": 64, "height": 64, "format": "PNG"},
        "layers": [],
        "network": {"name": "base", "chainId": 8453},
        "ipfs": {"provider": "pinata", "gateway": "https://gateway.pinata.cloud/ipfs/"},
    }
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")


# ── update_config_base_uri ────────────────────────────────────────────────────


class TestUpdateConfigBaseUri:
    def test_updates_base_uri(self, tmp_path):
        from src.utils import update_config_base_uri

        config_path = tmp_path / "config.json"
        _write_config(config_path)

        update_config_base_uri(str(config_path), "QmNewCID")

        with open(config_path, encoding="utf-8") as fh:
            updated = json.load(fh)

        assert updated["collection"]["baseUri"] == "ipfs://QmNewCID/"

    def test_preserves_other_fields(self, tmp_path):
        from src.utils import update_config_base_uri

        config_path = tmp_path / "config.json"
        _write_config(config_path)

        update_config_base_uri(str(config_path), "QmNewCID")

        with open(config_path, encoding="utf-8") as fh:
            updated = json.load(fh)

        assert updated["collection"]["name"] == "Test"
        assert updated["collection"]["symbol"] == "TST"
        assert updated["image"]["width"] == 64


# ── cmd_deploy ────────────────────────────────────────────────────────────────


class TestCmdDeploy:
    def _args(self, tmp_path: Path, network: str = "base-sepolia") -> Namespace:
        return Namespace(
            config=str(tmp_path / "config.json"),
            output=str(tmp_path / "output"),
            network=network,
        )

    def test_returns_1_when_cids_missing(self, tmp_path):
        from src.main import cmd_deploy

        args = self._args(tmp_path)
        assert cmd_deploy(args) == 1

    def test_returns_1_when_metadata_cid_absent(self, tmp_path):
        from src.main import cmd_deploy

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        (output_dir / "cids.json").write_text(
            json.dumps({"imagesCid": "QmImg"}), encoding="utf-8"
        )
        args = self._args(tmp_path)
        assert cmd_deploy(args) == 1

    def test_updates_config_and_calls_hardhat(self, tmp_path):
        from src.main import cmd_deploy

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _write_cids(output_dir, metadata_cid="QmMeta123")
        config_path = tmp_path / "config.json"
        _write_config(config_path)

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            rc = cmd_deploy(self._args(tmp_path))

        assert rc == 0
        mock_run.assert_called_once()
        cmd_args = mock_run.call_args[0][0]
        assert "hardhat" in cmd_args
        assert "--network" in cmd_args
        assert "base-sepolia" in cmd_args

        # Verify config.json was updated with the new CID
        with open(config_path, encoding="utf-8") as fh:
            updated = json.load(fh)
        assert updated["collection"]["baseUri"] == "ipfs://QmMeta123/"

    def test_respects_network_argument(self, tmp_path):
        from src.main import cmd_deploy

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _write_cids(output_dir)
        _write_config(tmp_path / "config.json")

        mock_result = MagicMock()
        mock_result.returncode = 0

        with patch("subprocess.run", return_value=mock_result) as mock_run:
            args = self._args(tmp_path, network="base")
            rc = cmd_deploy(args)

        assert rc == 0
        cmd_args = mock_run.call_args[0][0]
        assert "base" in cmd_args

    def test_propagates_nonzero_returncode(self, tmp_path):
        from src.main import cmd_deploy

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _write_cids(output_dir)
        _write_config(tmp_path / "config.json")

        mock_result = MagicMock()
        mock_result.returncode = 2

        with patch("subprocess.run", return_value=mock_result):
            rc = cmd_deploy(self._args(tmp_path))

        assert rc == 2

    def test_returns_1_when_npx_not_found(self, tmp_path):
        from src.main import cmd_deploy

        output_dir = tmp_path / "output"
        output_dir.mkdir()
        _write_cids(output_dir)
        _write_config(tmp_path / "config.json")

        with patch("subprocess.run", side_effect=FileNotFoundError):
            rc = cmd_deploy(self._args(tmp_path))

        assert rc == 1


# ── build_parser (deploy subcommand) ──────────────────────────────────────────


class TestBuildParser:
    def test_deploy_subcommand_registered(self):
        from src.main import build_parser

        parser = build_parser()
        args = parser.parse_args(["deploy", "--network", "base"])
        assert args.command == "deploy"
        assert args.network == "base"

    def test_deploy_defaults(self):
        from src.main import build_parser

        parser = build_parser()
        args = parser.parse_args(["deploy"])
        assert args.network == "base-sepolia"
        assert args.config == "config.json"
        assert args.output == "output"

    def test_run_network_option(self):
        from src.main import build_parser

        parser = build_parser()
        args = parser.parse_args(["run", "--network", "base"])
        assert args.network == "base"

    def test_run_default_network(self):
        from src.main import build_parser

        parser = build_parser()
        args = parser.parse_args(["run"])
        assert args.network == "base-sepolia"
