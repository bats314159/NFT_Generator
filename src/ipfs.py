"""
ipfs.py – IPFS upload integration.

Supports uploading images and metadata to IPFS via the Pinata pinning
service.  Set the environment variables ``PINATA_API_KEY`` and
``PINATA_API_SECRET`` (or ``PINATA_JWT``) before calling the upload
helpers.

Usage example::

    from src.ipfs import PinataClient

    client = PinataClient()
    images_cid  = client.upload_folder("output/images",  name="my-nft-images")
    metadata_cid = client.upload_folder("output/metadata", name="my-nft-metadata")
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests


_PINATA_BASE_URL = "https://api.pinata.cloud"
_PINATA_PIN_JSON_URL = f"{_PINATA_BASE_URL}/pinning/pinJSONToIPFS"
_PINATA_PIN_FILE_URL = f"{_PINATA_BASE_URL}/pinning/pinFileToIPFS"
_PINATA_TEST_AUTH_URL = f"{_PINATA_BASE_URL}/data/testAuthentication"


class IPFSUploadError(RuntimeError):
    """Raised when an IPFS upload operation fails."""


class PinataClient:
    """
    Thin wrapper around the Pinata REST API.

    Authentication is read from environment variables at construction time:

    * ``PINATA_JWT``         – Bearer JWT (recommended)
    * ``PINATA_API_KEY`` + ``PINATA_API_SECRET`` – legacy key/secret pair
    """

    def __init__(self) -> None:
        jwt = os.environ.get("PINATA_JWT")
        api_key = os.environ.get("PINATA_API_KEY")
        api_secret = os.environ.get("PINATA_API_SECRET")

        if jwt:
            self._headers: dict[str, str] = {"Authorization": f"Bearer {jwt}"}
        elif api_key and api_secret:
            self._headers = {
                "pinata_api_key": api_key,
                "pinata_secret_api_key": api_secret,
            }
        else:
            raise EnvironmentError(
                "Pinata credentials not found. "
                "Set PINATA_JWT or both PINATA_API_KEY and PINATA_API_SECRET."
            )

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def test_authentication(self) -> bool:
        """Return True if the credentials are valid."""
        resp = requests.get(_PINATA_TEST_AUTH_URL, headers=self._headers, timeout=15)
        return resp.status_code == 200

    def pin_json(self, data: dict[str, Any], name: str) -> str:
        """
        Pin *data* as a JSON file on IPFS.

        Returns the resulting IPFS CID.
        """
        payload = {
            "pinataContent": data,
            "pinataMetadata": {"name": name},
        }
        headers = {**self._headers, "Content-Type": "application/json"}
        resp = requests.post(
            _PINATA_PIN_JSON_URL,
            data=json.dumps(payload),
            headers=headers,
            timeout=30,
        )
        if resp.status_code != 200:
            raise IPFSUploadError(
                f"Failed to pin JSON '{name}': {resp.status_code} {resp.text}"
            )
        return resp.json()["IpfsHash"]

    def pin_file(self, file_path: str, name: str) -> str:
        """
        Pin a single file on IPFS.

        Returns the resulting IPFS CID.
        """
        path = Path(file_path)
        with open(path, "rb") as fh:
            files = {"file": (path.name, fh)}
            metadata = json.dumps({"name": name})
            resp = requests.post(
                _PINATA_PIN_FILE_URL,
                files=files,
                data={"pinataMetadata": metadata},
                headers=self._headers,
                timeout=60,
            )
        if resp.status_code != 200:
            raise IPFSUploadError(
                f"Failed to pin file '{file_path}': {resp.status_code} {resp.text}"
            )
        return resp.json()["IpfsHash"]

    def upload_folder(self, folder_path: str, name: str) -> str:
        """
        Upload all files in *folder_path* as a single IPFS directory.

        The files are uploaded as a multi-part form request so that they
        share a single CID root directory.  Returns the root CID.
        """
        folder = Path(folder_path)
        if not folder.is_dir():
            raise FileNotFoundError(f"Folder not found: {folder_path}")

        files_to_upload = sorted(folder.iterdir())
        if not files_to_upload:
            raise IPFSUploadError(f"Folder is empty: {folder_path}")

        file_handles = []
        multipart_files = []
        try:
            for file_path in files_to_upload:
                if file_path.is_file():
                    fh = open(file_path, "rb")  # noqa: WPS515
                    file_handles.append(fh)
                    multipart_files.append(
                        ("file", (f"{folder.name}/{file_path.name}", fh))
                    )

            metadata = json.dumps({"name": name})
            resp = requests.post(
                _PINATA_PIN_FILE_URL,
                files=multipart_files,
                data={"pinataMetadata": metadata},
                headers=self._headers,
                timeout=120,
            )
        finally:
            for fh in file_handles:
                fh.close()

        if resp.status_code != 200:
            raise IPFSUploadError(
                f"Failed to upload folder '{folder_path}': {resp.status_code} {resp.text}"
            )
        return resp.json()["IpfsHash"]

    def upload_images_and_metadata(
        self,
        images_dir: str,
        metadata_dir: str,
        collection_name: str,
    ) -> tuple[str, str]:
        """
        Convenience method: upload images folder then metadata folder.

        Returns ``(images_cid, metadata_cid)``.
        """
        images_cid = self.upload_folder(images_dir, name=f"{collection_name}-images")
        metadata_cid = self.upload_folder(
            metadata_dir, name=f"{collection_name}-metadata"
        )
        return images_cid, metadata_cid
