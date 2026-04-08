/**
 * utils.ts – shared frontend utilities.
 */

/**
 * Return the deployed contract address from the environment.
 * Throws at runtime if the variable is not set, so misconfiguration is caught
 * immediately rather than silently calling the zero address.
 */
export function getContractAddress(): `0x${string}` {
  const addr = process.env.NEXT_PUBLIC_CONTRACT_ADDRESS;
  if (!addr || addr === "0x0000000000000000000000000000000000000000") {
    throw new Error(
      "NEXT_PUBLIC_CONTRACT_ADDRESS is not set. " +
        "Copy .env.local.example to .env.local and fill in the deployed address."
    );
  }
  return addr as `0x${string}`;
}

/**
 * Return the correct Basescan transaction URL for the current chain.
 * Reads NEXT_PUBLIC_CHAIN_ID (8453 = Base mainnet, 84532 = Base Sepolia).
 */
export function basescanTxUrl(txHash: string): string {
  const chainId = parseInt(process.env.NEXT_PUBLIC_CHAIN_ID ?? "84532", 10);
  const base =
    chainId === 8453 ? "https://basescan.org" : "https://sepolia.basescan.org";
  return `${base}/tx/${txHash}`;
}
