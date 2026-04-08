"use client";

import { useState } from "react";
import { useAccount } from "wagmi";
import { publicMint, waitForMint } from "@/lib/contract";
import { basescanTxUrl } from "@/lib/utils";

interface Props {
  tokenURI: string;
  mintPrice: bigint;
  onMinted?: (txHash: `0x${string}`) => void;
}

type Status = "idle" | "confirm" | "pending" | "success" | "error";

/**
 * MintButton – calls `publicMint(tokenURI)` on the NFTCollection contract.
 *
 * Props
 * -----
 * tokenURI   – the IPFS metadata URI returned by the backend generator
 * mintPrice  – mint price in wei (read from contract via `getMintPrice()`)
 * onMinted   – optional callback with the confirmed tx hash
 */
export function MintButton({ tokenURI, mintPrice, onMinted }: Props) {
  const { isConnected } = useAccount();
  const [status, setStatus] = useState<Status>("idle");
  const [txHash, setTxHash] = useState<`0x${string}` | null>(null);
  const [errorMsg, setErrorMsg] = useState("");

  async function handleMint() {
    if (!isConnected) return;
    setStatus("confirm");
    setErrorMsg("");
    try {
      const hash = await publicMint(tokenURI, mintPrice);
      setTxHash(hash);
      setStatus("pending");
      await waitForMint(hash);
      setStatus("success");
      onMinted?.(hash);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Transaction failed";
      setErrorMsg(msg.length > 120 ? msg.slice(0, 120) + "…" : msg);
      setStatus("error");
    }
  }

  if (!isConnected) {
    return (
      <p style={styles.hint}>Connect your wallet to mint this NFT.</p>
    );
  }

  if (status === "success" && txHash) {
    return (
      <div style={styles.success}>
        <span>🎉 Minted!</span>
        <a
          href={basescanTxUrl(txHash)}
          target="_blank"
          rel="noreferrer"
          style={styles.link}
        >
          View on Basescan ↗
        </a>
      </div>
    );
  }

  const label: Record<Status, string> = {
    idle:    "Mint NFT",
    confirm: "Waiting for wallet…",
    pending: "Transaction pending…",
    success: "Minted!",
    error:   "Retry Mint",
  };

  return (
    <div style={styles.container}>
      <button
        onClick={handleMint}
        disabled={status === "confirm" || status === "pending"}
        style={{
          ...styles.button,
          opacity: status === "confirm" || status === "pending" ? 0.7 : 1,
        }}
      >
        {label[status]}
      </button>

      {mintPrice > 0n && (
        <p style={styles.price}>
          Price: {(Number(mintPrice) / 1e18).toFixed(4)} ETH
        </p>
      )}

      {status === "error" && (
        <p style={styles.error}>⚠ {errorMsg}</p>
      )}
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    gap: "8px",
  },
  hint: {
    color: "#777",
    fontSize: "0.9rem",
    textAlign: "center" as const,
  },
  button: {
    padding: "12px 32px",
    borderRadius: "10px",
    border: "none",
    background: "#0052ff",
    color: "#fff",
    fontWeight: 700,
    fontSize: "1rem",
    cursor: "pointer",
  } as React.CSSProperties,
  price: {
    fontSize: "0.85rem",
    color: "#555",
    margin: 0,
  },
  error: {
    color: "#c0392b",
    fontSize: "0.85rem",
    textAlign: "center" as const,
    maxWidth: "320px",
  },
  success: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    gap: "6px",
    color: "#27ae60",
    fontWeight: 700,
  },
  link: {
    color: "#0052ff",
    fontSize: "0.875rem",
  },
};
