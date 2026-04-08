"use client";

import { useAccount, useConnect, useDisconnect } from "wagmi";

/**
 * WalletButton – connect / disconnect an injected wallet (MetaMask, Coinbase
 * Wallet, Rabby, etc.).
 *
 * Shows a truncated address when connected, or a "Connect Wallet" prompt when
 * disconnected.
 */
export function WalletButton() {
  const { address, isConnected } = useAccount();
  const { connect, connectors, isPending } = useConnect();
  const { disconnect } = useDisconnect();

  if (isConnected && address) {
    const short = `${address.slice(0, 6)}…${address.slice(-4)}`;
    return (
      <button
        onClick={() => disconnect()}
        style={styles.button}
        title={address}
      >
        {short} · Disconnect
      </button>
    );
  }

  const injected = connectors.find((c) => c.id === "injected");

  return (
    <button
      onClick={() => injected && connect({ connector: injected })}
      disabled={isPending || !injected}
      style={styles.button}
    >
      {isPending ? "Connecting…" : "Connect Wallet"}
    </button>
  );
}

const styles = {
  button: {
    padding: "8px 16px",
    borderRadius: "8px",
    border: "1px solid #ccc",
    background: "#fff",
    cursor: "pointer",
    fontWeight: 600,
    fontSize: "0.9rem",
  } as React.CSSProperties,
};
