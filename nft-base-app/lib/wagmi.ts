import { http, createConfig } from "wagmi";
import { base, baseSepolia } from "wagmi/chains";
import { injected } from "wagmi/connectors";

/**
 * Wagmi config targeting Base and Base Sepolia.
 *
 * Connectors:
 *   - injected  → MetaMask, Coinbase Wallet, Rabby, etc.
 *
 * Set NEXT_PUBLIC_CHAIN_ID=8453 for mainnet or 84532 for Sepolia.
 */
export const wagmiConfig = createConfig({
  chains: [base, baseSepolia],
  connectors: [injected()],
  transports: {
    [base.id]:        http(),
    [baseSepolia.id]: http(),
  },
});
