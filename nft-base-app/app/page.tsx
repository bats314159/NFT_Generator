"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { WalletButton } from "@/components/WalletButton";
import { getCollectionInfo, type CollectionInfo } from "@/lib/api";
import { getTotalSupply, getMaxSupply } from "@/lib/contract";

/**
 * Home page – shows collection info and entry point to the generate/mint flow.
 */
export default function HomePage() {
  const [info, setInfo] = useState<CollectionInfo | null>(null);
  const [totalSupply, setTotalSupply] = useState<bigint | null>(null);
  const [maxSupply, setMaxSupply] = useState<bigint | null>(null);
  const [backendError, setBackendError] = useState(false);

  useEffect(() => {
    getCollectionInfo()
      .then(setInfo)
      .catch(() => setBackendError(true));

    getTotalSupply()
      .then(setTotalSupply)
      .catch(() => null);

    getMaxSupply()
      .then(setMaxSupply)
      .catch(() => null);
  }, []);

  return (
    <div style={styles.page}>
      {/* ── Header ─────────────────────────────────────────────── */}
      <header style={styles.header}>
        <span style={styles.logo}>🎨 NFT Generator</span>
        <WalletButton />
      </header>

      {/* ── Hero ───────────────────────────────────────────────── */}
      <main style={styles.main}>
        {backendError && (
          <p style={styles.warning}>
            ⚠ Backend not reachable. Start the server with{" "}
            <code>uvicorn server:app --reload</code> in{" "}
            <code>nft-base-app/backend/</code>.
          </p>
        )}

        <h1 style={styles.title}>
          {info ? info.name : "NFT Generator"}
        </h1>

        <p style={styles.description}>
          {info
            ? info.description
            : "Generate unique NFTs on Base — no two are alike."}
        </p>

        {/* Supply bar */}
        {totalSupply !== null && maxSupply !== null && (
          <p style={styles.supply}>
            {totalSupply.toString()} / {maxSupply.toString()} minted
          </p>
        )}

        <div style={styles.actions}>
          <Link href="/generate" style={styles.cta}>
            ✨ Generate &amp; Mint
          </Link>
        </div>

        {/* Collection meta */}
        {info && (
          <div style={styles.metaGrid}>
            <MetaItem label="Symbol" value={info.symbol} />
            <MetaItem label="Max Supply" value={info.size.toString()} />
            <MetaItem
              label="Royalty"
              value={`${(info.royaltyBps / 100).toFixed(1)}%`}
            />
          </div>
        )}
      </main>
    </div>
  );
}

function MetaItem({ label, value }: { label: string; value: string }) {
  return (
    <div style={metaStyles.item}>
      <span style={metaStyles.label}>{label}</span>
      <span style={metaStyles.value}>{value}</span>
    </div>
  );
}

const styles = {
  page: { minHeight: "100vh", background: "#f8f9ff" },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "16px 32px",
    borderBottom: "1px solid #e8e8e8",
    background: "#fff",
  },
  logo: { fontWeight: 700, fontSize: "1.15rem" },
  main: {
    display: "flex",
    flexDirection: "column" as const,
    alignItems: "center",
    gap: "20px",
    padding: "60px 24px",
    maxWidth: "600px",
    margin: "0 auto",
    textAlign: "center" as const,
  },
  title: { fontSize: "2.4rem", fontWeight: 800, margin: 0, color: "#111" },
  description: { fontSize: "1.1rem", color: "#555", margin: 0, lineHeight: 1.6 },
  supply: { color: "#0052ff", fontWeight: 600, margin: 0 },
  actions: { display: "flex", gap: "12px" },
  cta: {
    padding: "14px 32px",
    borderRadius: "12px",
    background: "#0052ff",
    color: "#fff",
    fontWeight: 700,
    fontSize: "1.05rem",
    textDecoration: "none",
    display: "inline-block",
  } as React.CSSProperties,
  metaGrid: {
    display: "flex",
    gap: "16px",
    flexWrap: "wrap" as const,
    justifyContent: "center",
  },
  warning: {
    background: "#fff3cd",
    border: "1px solid #ffc107",
    borderRadius: "8px",
    padding: "12px 16px",
    fontSize: "0.875rem",
    color: "#856404",
    margin: 0,
  },
};

const metaStyles = {
  item: {
    background: "#fff",
    border: "1px solid #e0e0e0",
    borderRadius: "10px",
    padding: "12px 20px",
    display: "flex",
    flexDirection: "column" as const,
    gap: "4px",
    minWidth: "100px",
  },
  label: { fontSize: "0.72rem", color: "#0052ff", fontWeight: 700, textTransform: "uppercase" as const },
  value: { fontSize: "1rem", fontWeight: 700, color: "#111" },
};
