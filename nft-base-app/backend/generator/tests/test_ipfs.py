"""
tests/test_ipfs.py – Unit tests for src/ipfs.py (using mocked HTTP responses)
"""

from __future__ import annotations

import json
import os
from unittest.mock import patch, MagicMock

import pytest
import responses as resp_lib


# ── PinataClient construction ─────────────────────────────────────────────────


class TestPinataClientInit:
    def test_jwt_auth(self, monkeypatch):
        monkeypatch.setenv("PINATA_JWT", "my-jwt-token")
        monkeypatch.delenv("PINATA_API_KEY", raising=False)
        monkeypatch.delenv("PINATA_API_SECRET", raising=False)
        from src.ipfs import PinataClient

        client = PinataClient()
        assert "Authorization" in client._headers
        assert client._headers["Authorization"] == "Bearer my-jwt-token"

    def test_api_key_auth(self, monkeypatch):
        monkeypatch.delenv("PINATA_JWT", raising=False)
        monkeypatch.setenv("PINATA_API_KEY", "key123")
        monkeypatch.setenv("PINATA_API_SECRET", "secret456")
        from src.ipfs import PinataClient

        client = PinataClient()
        assert "pinata_api_key" in client._headers

    def test_no_credentials_raises(self, monkeypatch):
        monkeypatch.delenv("PINATA_JWT", raising=False)
        monkeypatch.delenv("PINATA_API_KEY", raising=False)
        monkeypatch.delenv("PINATA_API_SECRET", raising=False)
        from src.ipfs import PinataClient

        with pytest.raises(EnvironmentError, match="Pinata credentials"):
            PinataClient()


# ── pin_json ──────────────────────────────────────────────────────────────────


class TestPinJson:
    @resp_lib.activate
    def test_returns_cid_on_success(self, monkeypatch):
        monkeypatch.setenv("PINATA_JWT", "test-jwt")
        monkeypatch.delenv("PINATA_API_KEY", raising=False)
        monkeypatch.delenv("PINATA_API_SECRET", raising=False)

        resp_lib.add(
            resp_lib.POST,
            "https://api.pinata.cloud/pinning/pinJSONToIPFS",
            json={"IpfsHash": "QmTestCID123"},
            status=200,
        )

        from src.ipfs import PinataClient

        client = PinataClient()
        cid = client.pin_json({"key": "value"}, name="test.json")
        assert cid == "QmTestCID123"

    @resp_lib.activate
    def test_raises_on_error_status(self, monkeypatch):
        monkeypatch.setenv("PINATA_JWT", "test-jwt")
        monkeypatch.delenv("PINATA_API_KEY", raising=False)
        monkeypatch.delenv("PINATA_API_SECRET", raising=False)

        resp_lib.add(
            resp_lib.POST,
            "https://api.pinata.cloud/pinning/pinJSONToIPFS",
            json={"error": "Unauthorized"},
            status=401,
        )

        from src.ipfs import PinataClient, IPFSUploadError

        client = PinataClient()
        with pytest.raises(IPFSUploadError, match="Failed to pin JSON"):
            client.pin_json({"key": "value"}, name="test.json")


# ── upload_folder ─────────────────────────────────────────────────────────────


class TestUploadFolder:
    @resp_lib.activate
    def test_uploads_folder_returns_cid(self, tmp_path, monkeypatch):
        monkeypatch.setenv("PINATA_JWT", "test-jwt")
        monkeypatch.delenv("PINATA_API_KEY", raising=False)
        monkeypatch.delenv("PINATA_API_SECRET", raising=False)

        # Create some files in a temp folder
        (tmp_path / "1.png").write_bytes(b"\x89PNG")
        (tmp_path / "2.png").write_bytes(b"\x89PNG")

        resp_lib.add(
            resp_lib.POST,
            "https://api.pinata.cloud/pinning/pinFileToIPFS",
            json={"IpfsHash": "QmFolderCID"},
            status=200,
        )

        from src.ipfs import PinataClient

        client = PinataClient()
        cid = client.upload_folder(str(tmp_path), name="test-folder")
        assert cid == "QmFolderCID"

    def test_raises_for_nonexistent_folder(self, monkeypatch):
        monkeypatch.setenv("PINATA_JWT", "test-jwt")
        monkeypatch.delenv("PINATA_API_KEY", raising=False)
        monkeypatch.delenv("PINATA_API_SECRET", raising=False)

        from src.ipfs import PinataClient

        client = PinataClient()
        with pytest.raises(FileNotFoundError):
            client.upload_folder("/nonexistent/path/folder", name="test")

    @resp_lib.activate
    def test_raises_for_empty_folder(self, tmp_path, monkeypatch):
        monkeypatch.setenv("PINATA_JWT", "test-jwt")
        monkeypatch.delenv("PINATA_API_KEY", raising=False)
        monkeypatch.delenv("PINATA_API_SECRET", raising=False)

        from src.ipfs import PinataClient, IPFSUploadError

        client = PinataClient()
        with pytest.raises(IPFSUploadError, match="empty"):
            client.upload_folder(str(tmp_path), name="empty-folder")
