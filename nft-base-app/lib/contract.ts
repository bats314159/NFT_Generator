import { readContract, writeContract, waitForTransactionReceipt } from "wagmi/actions";
import { wagmiConfig } from "./wagmi";
import { NFT_COLLECTION_ABI } from "@/contracts/abi";
import { getContractAddress } from "./utils";

/**
 * Deployed contract address – read from NEXT_PUBLIC_CONTRACT_ADDRESS.
 * Throws if the variable is unset or is the zero address.
 */
export function getAddress(): `0x${string}` {
  return getContractAddress();
}

export { NFT_COLLECTION_ABI as CONTRACT_ABI };

// ── Read helpers ─────────────────────────────────────────────────────────────

export async function getTotalSupply(): Promise<bigint> {
  return readContract(wagmiConfig, {
    address: getAddress(),
    abi: NFT_COLLECTION_ABI,
    functionName: "totalSupply",
  });
}

export async function getMaxSupply(): Promise<bigint> {
  return readContract(wagmiConfig, {
    address: getAddress(),
    abi: NFT_COLLECTION_ABI,
    functionName: "MAX_SUPPLY",
  });
}

export async function getMintPrice(): Promise<bigint> {
  return readContract(wagmiConfig, {
    address: getAddress(),
    abi: NFT_COLLECTION_ABI,
    functionName: "mintPrice",
  });
}

export async function isPaused(): Promise<boolean> {
  return readContract(wagmiConfig, {
    address: getAddress(),
    abi: NFT_COLLECTION_ABI,
    functionName: "paused",
  });
}

// ── Write helpers ─────────────────────────────────────────────────────────────

/**
 * Call `publicMint(tokenURI_)` on the contract.
 * Returns the transaction hash.
 */
export async function publicMint(tokenURI: string, value: bigint): Promise<`0x${string}`> {
  const hash = await writeContract(wagmiConfig, {
    address: getAddress(),
    abi: NFT_COLLECTION_ABI,
    functionName: "publicMint",
    args: [tokenURI],
    value,
  });
  return hash;
}

/**
 * Wait for a mint transaction to be confirmed and return the receipt.
 */
export async function waitForMint(hash: `0x${string}`) {
  return waitForTransactionReceipt(wagmiConfig, { hash });
}
