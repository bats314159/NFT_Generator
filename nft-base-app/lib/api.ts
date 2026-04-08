/**
 * api.ts – TypeScript client for the FastAPI backend generator service.
 *
 * The backend runs at NEXT_PUBLIC_API_URL (default: http://localhost:8000).
 */

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface NFTAttribute {
  trait_type: string;
  value: string;
}

export interface GenerateResult {
  /** IPFS token URI to pass to publicMint() */
  tokenURI: string;
  /** HTTPS gateway URL suitable for <img> tags */
  imageUrl: string;
  attributes: NFTAttribute[];
  metadata: Record<string, unknown>;
}

export interface CollectionInfo {
  name: string;
  description: string;
  symbol: string;
  size: number;
  baseUri: string;
  royaltyBps: number;
}

// ── Requests ──────────────────────────────────────────────────────────────────

/**
 * Fetch collection metadata from the backend.
 * Reads config.json without any IPFS calls.
 */
export async function getCollectionInfo(): Promise<CollectionInfo> {
  const res = await fetch(`${API_BASE}/api/collection`);
  if (!res.ok) {
    throw new Error(`Failed to fetch collection info: ${res.status} ${res.statusText}`);
  }
  return res.json() as Promise<CollectionInfo>;
}

/**
 * Ask the backend to generate one unique NFT, upload it to IPFS, and return
 * the token URI + preview data.
 *
 * Requires PINATA_JWT (or PINATA_API_KEY + PINATA_API_SECRET) to be set in the
 * backend environment.
 */
export async function generateNFT(): Promise<GenerateResult> {
  const res = await fetch(`${API_BASE}/api/generate`, { method: "POST" });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`NFT generation failed: ${res.status} ${body}`);
  }
  return res.json() as Promise<GenerateResult>;
}
