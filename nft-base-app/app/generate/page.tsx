"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { WalletButton } from "@/components/WalletButton";
import { GenerateForm } from "@/components/GenerateForm";
import { PreviewCard } from "@/components/PreviewCard";
import { MintButton } from "@/components/MintButton";
import { getMintPrice } from "@/lib/contract";
import { basescanTxUrl } from "@/lib/utils";
import type { GenerateResult } from "@/lib/api";

type Step = "generate" | "preview" | "minted";

/**
 * /generate – the main on-demand NFT generation and minting page.
 *
 * Flow:
 *   1. User clicks "Generate NFT"  → backend creates image, uploads to IPFS
 *   2. Preview + traits are shown
 *   3. User clicks "Mint NFT"      → wallet prompts for the tx
 *   4. On confirmation             → success state with tx link
 */
export default function GeneratePage() {
  const [step, setStep] = useState<Step>("generate");
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [mintPrice, setMintPrice] = useState<bigint>(0n);
  const [txHash, setTxHash] = useState<`0x${string}` | null>(null);

  useEffect(() => {
    getMintPrice()
      .then(setMintPrice)
      .catch(() => setMintPrice(0n));
  }, []);

  function handleGenerated(r: GenerateResult) {
    setResult(r);
    setStep("preview");
  }

  function handleMinted(hash: `0x${string}`) {
    setTxHash(hash);
    setStep("minted");
  }

  return (
    <div style={styles.page}>
      {/* ── Header ─────────────────────────────────────────────── */}
      <header style={styles.header}>
        <Link href="/" style={styles.back}>
          ← Back
        </Link>
        <span style={styles.title}>Generate &amp; Mint</span>
        <WalletButton />
      </header>

      <main style={styles.main}>
        {/* ── Step 1: Generate ────────────────────────────────── */}
        {step === "generate" && (
          <section style={styles.section}>
            <h2 style={styles.sectionTitle}>Create your NFT</h2>
            <GenerateForm onGenerated={handleGenerated} />
          </section>
        )}

        {/* ── Step 2: Preview + Mint ──────────────────────────── */}
        {step === "preview" && result && (
          <section style={styles.section}>
            <h2 style={styles.sectionTitle}>Your NFT</h2>
            <PreviewCard result={result} />

            <div style={styles.mintArea}>
              <MintButton
                tokenURI={result.tokenURI}
                mintPrice={mintPrice}
                onMinted={handleMinted}
              />
            </div>

            <button
              onClick={() => {
                setResult(null);
                setStep("generate");
              }}
              style={styles.regenerate}
            >
              ↩ Generate a different one
            </button>
          </section>
        )}

        {/* ── Step 3: Success ─────────────────────────────────── */}
        {step === "minted" && txHash && (
          <section style={{ ...styles.section, textAlign: "center" }}>
            <h2 style={{ ...styles.sectionTitle, color: "#27ae60" }}>
              🎉 NFT Minted!
            </h2>
            {result && <PreviewCard result={result} />}

            <p style={styles.txNote}>
              Transaction confirmed.{" "}
              <a
                href={basescanTxUrl(txHash)}
                target="_blank"
                rel="noreferrer"
                style={styles.link}
              >
                View on Basescan ↗
              </a>
            </p>

            <button
              onClick={() => {
                setResult(null);
                setTxHash(null);
                setStep("generate");
              }}
              style={styles.regenerate}
            >
              ✨ Mint another
            </button>
          </section>
        )}
      </main>
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
  back: { color: "#0052ff", textDecoration: "none", fontWeight: 600 },
  title: { fontWeight: 700, fontSize: "1.1rem" },
  main: {
    maxWidth: "520px",
    margin: "40px auto",
    padding: "0 24px",
    display: "flex",
    flexDirection: "column" as const,
    gap: "32px",
  },
  section: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "20px",
  },
  sectionTitle: {
    fontSize: "1.5rem",
    fontWeight: 800,
    margin: 0,
    textAlign: "center" as const,
  },
  mintArea: {
    display: "flex",
    justifyContent: "center",
    paddingTop: "8px",
  },
  regenerate: {
    alignSelf: "center",
    background: "transparent",
    border: "1px solid #ccc",
    borderRadius: "8px",
    padding: "8px 18px",
    cursor: "pointer",
    color: "#555",
    fontSize: "0.875rem",
  } as React.CSSProperties,
  txNote: { color: "#333", fontSize: "0.9rem" },
  link: { color: "#0052ff" },
};
