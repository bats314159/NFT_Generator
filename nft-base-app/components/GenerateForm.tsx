"use client";

import { useState } from "react";
import { generateNFT, type GenerateResult } from "@/lib/api";

interface Props {
  onGenerated: (result: GenerateResult) => void;
}

type Status = "idle" | "generating" | "error";

/**
 * GenerateForm – triggers an on-demand NFT generation via the backend API.
 *
 * On success it calls `onGenerated` with the result so a parent component
 * can display the preview and enable minting.
 */
export function GenerateForm({ onGenerated }: Props) {
  const [status, setStatus] = useState<Status>("idle");
  const [errorMsg, setErrorMsg] = useState("");

  async function handleGenerate() {
    setStatus("generating");
    setErrorMsg("");
    try {
      const result = await generateNFT();
      setStatus("idle");
      onGenerated(result);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Unknown error");
      setStatus("error");
    }
  }

  return (
    <div style={styles.container}>
      <p style={styles.hint}>
        Click <strong>Generate</strong> to create a unique NFT. The backend will
        pick a random trait combination, composite the image, and upload
        everything to IPFS. You can then mint it to your wallet.
      </p>

      <button
        onClick={handleGenerate}
        disabled={status === "generating"}
        style={{
          ...styles.button,
          opacity: status === "generating" ? 0.7 : 1,
        }}
      >
        {status === "generating" ? "Generating…" : "✨ Generate NFT"}
      </button>

      {status === "error" && (
        <p style={styles.error}>
          ⚠ {errorMsg}
          <br />
          <small>Make sure the backend server is running and IPFS credentials are set.</small>
        </p>
      )}
    </div>
  );
}

const styles = {
  container: {
    display: "flex",
    flexDirection: "column" as const,
    gap: "12px",
    alignItems: "center",
    padding: "24px",
    border: "1px solid #e0e0e0",
    borderRadius: "12px",
    background: "#fafafa",
    maxWidth: "480px",
    margin: "0 auto",
  },
  hint: {
    textAlign: "center" as const,
    color: "#555",
    fontSize: "0.95rem",
    margin: 0,
  },
  button: {
    padding: "12px 28px",
    borderRadius: "10px",
    border: "none",
    background: "#0052ff",
    color: "#fff",
    fontWeight: 700,
    fontSize: "1rem",
    cursor: "pointer",
  } as React.CSSProperties,
  error: {
    color: "#c0392b",
    fontSize: "0.875rem",
    textAlign: "center" as const,
  },
};
