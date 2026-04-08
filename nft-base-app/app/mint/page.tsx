"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Suspense } from "react";
import { basescanTxUrl } from "@/lib/utils";

/**
 * /mint – confirmation page shown after a successful mint.
 *
 * Query params:
 *   txHash   – transaction hash
 *   tokenId  – (optional) minted token ID
 */
function MintContent() {
  const params = useSearchParams();
  const txHash = params.get("txHash");
  const tokenId = params.get("tokenId");

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.icon}>🎉</div>
        <h1 style={styles.title}>NFT Minted!</h1>

        {tokenId && (
          <p style={styles.detail}>Token ID: <strong>#{tokenId}</strong></p>
        )}

        {txHash ? (
          <a
            href={basescanTxUrl(txHash)}
            target="_blank"
            rel="noreferrer"
            style={styles.link}
          >
            View transaction on Basescan ↗
          </a>
        ) : (
          <p style={styles.detail}>Your NFT is on its way to the blockchain.</p>
        )}

        <div style={styles.actions}>
          <Link href="/generate" style={styles.button}>
            ✨ Mint Another
          </Link>
          <Link href="/" style={styles.secondary}>
            ← Home
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function MintPage() {
  return (
    <Suspense>
      <MintContent />
    </Suspense>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    background: "#f8f9ff",
    padding: "24px",
  },
  card: {
    background: "#fff",
    borderRadius: "16px",
    padding: "48px 40px",
    textAlign: "center" as const,
    maxWidth: "420px",
    width: "100%",
    boxShadow: "0 4px 24px rgba(0,0,0,0.08)",
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    gap: "16px",
  },
  icon: { fontSize: "3rem" },
  title: { fontSize: "2rem", fontWeight: 800, margin: 0, color: "#111" },
  detail: { color: "#555", margin: 0, fontSize: "0.95rem" },
  link: { color: "#0052ff", fontWeight: 600, fontSize: "0.95rem" },
  actions: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "10px",
    width: "100%",
    paddingTop: "8px",
  },
  button: {
    padding: "12px 24px",
    borderRadius: "10px",
    background: "#0052ff",
    color: "#fff",
    fontWeight: 700,
    textDecoration: "none",
    display: "block",
    textAlign: "center" as const,
  } as React.CSSProperties,
  secondary: {
    padding: "10px 24px",
    borderRadius: "10px",
    border: "1px solid #ccc",
    color: "#555",
    fontWeight: 600,
    textDecoration: "none",
    display: "block",
    textAlign: "center" as const,
  } as React.CSSProperties,
};
