import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "NFT Generator",
  description:
    "Generate NFT collections with layer compositing, IPFS upload, and ERC-721 deployment on Base",
  other: {
    "application-name": "NFT Generator",
    ...(process.env.NEXT_PUBLIC_BASE_APP_ID
      ? { "base:app_id": process.env.NEXT_PUBLIC_BASE_APP_ID }
      : {}),
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
