/**
 * abi.ts – TypeScript ABI for NFTCollection.sol
 *
 * Generated from contracts/NFTCollection.sol.
 * Import this wherever you need to interact with the contract via wagmi/viem.
 */

export const NFT_COLLECTION_ABI = [
  // ── Constructor ────────────────────────────────────────────────────
  {
    type: "constructor",
    inputs: [
      { name: "name_",           type: "string"  },
      { name: "symbol_",         type: "string"  },
      { name: "maxSupply_",      type: "uint256" },
      { name: "baseTokenURI_",   type: "string"  },
      { name: "royaltyReceiver", type: "address" },
      { name: "royaltyBps_",     type: "uint96"  },
      { name: "contractURI_",    type: "string"  },
    ],
    stateMutability: "nonpayable",
  },

  // ── Public mint ────────────────────────────────────────────────────
  {
    type: "function",
    name: "publicMint",
    inputs:  [{ name: "tokenURI_", type: "string" }],
    outputs: [],
    stateMutability: "payable",
  },

  // ── Mint controls ──────────────────────────────────────────────────
  {
    type: "function",
    name: "mintPrice",
    inputs:  [],
    outputs: [{ type: "uint256" }],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "setMintPrice",
    inputs:  [{ name: "price", type: "uint256" }],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "paused",
    inputs:  [],
    outputs: [{ type: "bool" }],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "setPaused",
    inputs:  [{ name: "paused_", type: "bool" }],
    outputs: [],
    stateMutability: "nonpayable",
  },

  // ── Owner-only batch mint ──────────────────────────────────────────
  {
    type: "function",
    name: "mint",
    inputs:  [
      { name: "to",       type: "address" },
      { name: "quantity", type: "uint256" },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },

  // ── Supply ─────────────────────────────────────────────────────────
  {
    type: "function",
    name: "totalSupply",
    inputs:  [],
    outputs: [{ type: "uint256" }],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "MAX_SUPPLY",
    inputs:  [],
    outputs: [{ type: "uint256" }],
    stateMutability: "view",
  },

  // ── Metadata ───────────────────────────────────────────────────────
  {
    type: "function",
    name: "tokenURI",
    inputs:  [{ name: "tokenId", type: "uint256" }],
    outputs: [{ type: "string" }],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "baseURI",
    inputs:  [],
    outputs: [{ type: "string" }],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "setBaseURI",
    inputs:  [{ name: "newBaseURI", type: "string" }],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "contractURI",
    inputs:  [],
    outputs: [{ type: "string" }],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "setContractURI",
    inputs:  [{ name: "newContractURI", type: "string" }],
    outputs: [],
    stateMutability: "nonpayable",
  },

  // ── Ownership ──────────────────────────────────────────────────────
  {
    type: "function",
    name: "owner",
    inputs:  [],
    outputs: [{ type: "address" }],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "transferOwnership",
    inputs:  [{ name: "newOwner", type: "address" }],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "renounceOwnership",
    inputs:  [],
    outputs: [],
    stateMutability: "nonpayable",
  },

  // ── ERC-721 ────────────────────────────────────────────────────────
  {
    type: "function",
    name: "name",
    inputs:  [],
    outputs: [{ type: "string" }],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "symbol",
    inputs:  [],
    outputs: [{ type: "string" }],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "ownerOf",
    inputs:  [{ name: "tokenId", type: "uint256" }],
    outputs: [{ type: "address" }],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "balanceOf",
    inputs:  [{ name: "owner", type: "address" }],
    outputs: [{ type: "uint256" }],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "approve",
    inputs:  [
      { name: "to",      type: "address" },
      { name: "tokenId", type: "uint256" },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "setApprovalForAll",
    inputs:  [
      { name: "operator", type: "address" },
      { name: "approved", type: "bool"    },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "isApprovedForAll",
    inputs:  [
      { name: "owner",    type: "address" },
      { name: "operator", type: "address" },
    ],
    outputs: [{ type: "bool" }],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "transferFrom",
    inputs:  [
      { name: "from",    type: "address" },
      { name: "to",      type: "address" },
      { name: "tokenId", type: "uint256" },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "safeTransferFrom",
    inputs:  [
      { name: "from",    type: "address" },
      { name: "to",      type: "address" },
      { name: "tokenId", type: "uint256" },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
  {
    type: "function",
    name: "supportsInterface",
    inputs:  [{ name: "interfaceId", type: "bytes4" }],
    outputs: [{ type: "bool" }],
    stateMutability: "view",
  },

  // ── EIP-2981 Royalties ─────────────────────────────────────────────
  {
    type: "function",
    name: "royaltyInfo",
    inputs:  [
      { name: "tokenId",   type: "uint256" },
      { name: "salePrice", type: "uint256" },
    ],
    outputs: [
      { name: "receiver",      type: "address" },
      { name: "royaltyAmount", type: "uint256" },
    ],
    stateMutability: "view",
  },
  {
    type: "function",
    name: "setRoyalty",
    inputs:  [
      { name: "receiver", type: "address" },
      { name: "bps",      type: "uint96"  },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },

  // ── Financials ─────────────────────────────────────────────────────
  {
    type: "function",
    name: "withdraw",
    inputs:  [],
    outputs: [],
    stateMutability: "nonpayable",
  },

  // ── Events ─────────────────────────────────────────────────────────
  {
    type: "event",
    name: "Transfer",
    inputs: [
      { name: "from",    type: "address", indexed: true  },
      { name: "to",      type: "address", indexed: true  },
      { name: "tokenId", type: "uint256", indexed: true  },
    ],
  },
  {
    type: "event",
    name: "Approval",
    inputs: [
      { name: "owner",    type: "address", indexed: true  },
      { name: "approved", type: "address", indexed: true  },
      { name: "tokenId",  type: "uint256", indexed: true  },
    ],
  },
  {
    type: "event",
    name: "ApprovalForAll",
    inputs: [
      { name: "owner",    type: "address", indexed: true  },
      { name: "operator", type: "address", indexed: true  },
      { name: "approved", type: "bool",    indexed: false },
    ],
  },
  {
    type: "event",
    name: "BaseURIUpdated",
    inputs: [{ name: "newBaseURI", type: "string", indexed: false }],
  },
  {
    type: "event",
    name: "ContractURIUpdated",
    inputs: [{ name: "newContractURI", type: "string", indexed: false }],
  },
  {
    type: "event",
    name: "RoyaltyUpdated",
    inputs: [
      { name: "receiver", type: "address", indexed: false },
      { name: "bps",      type: "uint96",  indexed: false },
    ],
  },
  {
    type: "event",
    name: "MintPriceUpdated",
    inputs: [{ name: "newPrice", type: "uint256", indexed: false }],
  },
  {
    type: "event",
    name: "PauseStateUpdated",
    inputs: [{ name: "paused", type: "bool", indexed: false }],
  },
] as const;

export type NftCollectionAbi = typeof NFT_COLLECTION_ABI;
