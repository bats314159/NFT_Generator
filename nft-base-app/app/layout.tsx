import type { Metadata } from "next";
import { Providers } from "./providers";

export const metadata: Metadata = {
  title: "NFT Generator",
  description:
    "Generate unique NFT collections with layer compositing, IPFS upload, and ERC-721 minting on Base.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body style={{ margin: 0, fontFamily: "system-ui, sans-serif" }}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
