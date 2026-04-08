import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    // Allow IPFS gateway images in <Image> components
    remotePatterns: [
      {
        protocol: "https",
        hostname: "gateway.pinata.cloud",
        pathname: "/ipfs/**",
      },
      {
        protocol: "https",
        hostname: "ipfs.io",
        pathname: "/ipfs/**",
      },
    ],
  },
};

export default nextConfig;
