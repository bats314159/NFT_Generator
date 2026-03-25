# NFT Generator

A complete, end-to-end NFT collection generator that:

* **Combines PNG layers** into unique NFT images using Pillow
* **Generates ERC-721 metadata JSON** (OpenSea-compatible) with randomised traits and rarity weights
* **Uploads to IPFS** via the Pinata API
* **Deploys an ERC-721 smart contract** to Base (Mainnet or Sepolia), or any other EVM network

---

## Project structure

```
NFT_Generator/
├── config.json                   # Collection settings, layers, rarities
├── requirements.txt              # Python runtime deps (Pillow, requests)
├── requirements-dev.txt          # Dev deps (pytest, responses)
├── package.json                  # Hardhat / Solidity tooling
├── hardhat.config.js             # Hardhat config with Base network support
├── .env.example                  # Template for secrets
│
├── src/
│   ├── generator.py              # Layer compositing & image generation
│   ├── metadata.py               # ERC-721 JSON metadata generation
│   ├── ipfs.py                   # Pinata IPFS upload client
│   ├── main.py                   # CLI entry point
│   └── utils.py                  # Shared helpers
│
├── contracts/
│   └── NFTCollection.sol         # ERC-721 + EIP-2981 smart contract
│
├── scripts/
│   ├── deploy.js                 # Hardhat deployment script
│   └── create_sample_layers.py  # Generate placeholder layer PNGs
│
├── layers/                       # Place layer folders here (see below)
├── output/                       # Generated images & metadata (git-ignored)
└── tests/                        # Python unit tests
```

---

## Quick start

### 1 – Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # for running tests
```

### 2 – Configure your collection

Edit **`config.json`** to set your collection name, size, and define your
layers/traits with rarity weights.

### 3 – Add your layer artwork

Create sub-folders inside `layers/` that match the `"name"` of each layer in
`config.json`, then add a PNG file for each trait:

```
layers/
  Background/
    blue.png
    red.png
    ...
  Body/
    circle.png
    square.png
    ...
```

> **Tip** – run `python scripts/create_sample_layers.py` to auto-generate
> placeholder PNGs from `config.json` so you can try the generator immediately.

### 4 – Generate the collection

```bash
python -m src.main generate --config config.json --layers layers/ --output output/
```

Images are saved to `output/images/`, metadata JSON to `output/metadata/`, and
a rarity summary to `output/summary.json`.

### 5 – Upload to IPFS (Pinata)

Copy `.env.example` to `.env` and fill in your Pinata credentials, then:

```bash
python -m src.main upload --config config.json --output output/
```

The resulting IPFS CIDs are printed and saved to `output/cids.json`.

### 6 – Deploy the smart contract

Install Node dependencies:

```bash
npm install
```

Copy `.env.example` to `.env` and set `PRIVATE_KEY`, `BASE_RPC_URL`, and
optionally `BASESCAN_API_KEY`.

Update `config.json` → `collection.baseUri` with the metadata CID from step 5,
and `collection.contractUri` with the IPFS CID of your
[collection-level metadata JSON](https://docs.opensea.io/docs/contract-level-metadata)
(used by OpenSea and other Base marketplaces to display the collection name,
image, and description).  You can leave `contractUri` blank and call
`setContractURI()` on the contract later.

Then deploy to Base Sepolia (testnet) or Base Mainnet:

```bash
# Testnet
npx hardhat run scripts/deploy.js --network base-sepolia

# Mainnet
npx hardhat run scripts/deploy.js --network base
```

The contract address is printed and saved to `output/deployment-<network>.json`.

**Verify on Basescan** (the deploy script prints the exact command):

```bash
npx hardhat verify --network base <ADDRESS> "My NFT" "MNC" 10 "ipfs://Qm…/" "0x…" 500 "ipfs://QmContract"
```

---

## Running tests

```bash
pytest tests/ -v
```

---

## Smart contract

`contracts/NFTCollection.sol` is an **ERC-721** contract with:

| Feature | Details |
|---|---|
| Standard | ERC-721 (OpenZeppelin v5) |
| Metadata | `baseURI + tokenId + ".json"` |
| Collection metadata | `contractURI()` (OpenSea / Base marketplace standard) |
| Royalties | EIP-2981 (configurable bps) |
| Networks | Base Mainnet (8453), Base Sepolia (84532), any EVM |
| Supply cap | `MAX_SUPPLY` set at deploy time |
| Owner mint | `mint(address to, uint256 quantity)` |
| Reveal | `setBaseURI(string)` for delayed reveals |

---

## Environment variables

| Variable | Description |
|---|---|
| `PINATA_JWT` | Pinata Bearer JWT (recommended) |
| `PINATA_API_KEY` / `PINATA_API_SECRET` | Pinata legacy key pair |
| `PRIVATE_KEY` | Deployer wallet private key |
| `BASE_RPC_URL` | Base Mainnet RPC URL |
| `BASE_SEPOLIA_RPC_URL` | Base Sepolia RPC URL |
| `BASESCAN_API_KEY` | Basescan API key for verification |

> ⚠️ **Never commit your `.env` file.**  It is listed in `.gitignore`.
