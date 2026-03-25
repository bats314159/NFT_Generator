/**
 * deploy.js – Deployment script for NFTCollection.
 *
 * Configuration is read from environment variables (see .env.example).
 *
 * Usage:
 *   npx hardhat run scripts/deploy.js --network base-sepolia
 *   npx hardhat run scripts/deploy.js --network base
 *
 * After deployment, verify on Basescan with:
 *   npx hardhat verify --network base <CONTRACT_ADDRESS> <args...>
 */

const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with account:", deployer.address);

  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", ethers.formatEther(balance), "ETH");

  // ── Read config ──────────────────────────────────────────────────
  const configPath = path.join(__dirname, "..", "config.json");
  const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
  const col = config.collection;

  const name           = col.name;
  const symbol         = col.symbol;
  const maxSupply      = col.size;
  const baseTokenURI   = col.baseUri;
  const royaltyBps     = col.royaltyBps;
  const royaltyReceiver =
    col.royaltyReceiver !== "0x0000000000000000000000000000000000000000"
      ? col.royaltyReceiver
      : deployer.address;
  const contractURI    = col.contractUri || "";

  console.log("\nDeployment parameters:");
  console.log("  Name:            ", name);
  console.log("  Symbol:          ", symbol);
  console.log("  Max supply:      ", maxSupply);
  console.log("  Base URI:        ", baseTokenURI);
  console.log("  Contract URI:    ", contractURI || "(not set)");
  console.log("  Royalty receiver:", royaltyReceiver);
  console.log("  Royalty bps:     ", royaltyBps, `(${royaltyBps / 100}%)`);

  // ── Deploy ────────────────────────────────────────────────────────
  const NFTCollection = await ethers.getContractFactory("NFTCollection");
  const contract = await NFTCollection.deploy(
    name,
    symbol,
    maxSupply,
    baseTokenURI,
    royaltyReceiver,
    royaltyBps,
    contractURI
  );

  await contract.waitForDeployment();
  const address = await contract.getAddress();

  console.log("\nNFTCollection deployed to:", address);

  // ── Persist deployment info ───────────────────────────────────────
  const network = hre.network.name;
  const chainId = (await ethers.provider.getNetwork()).chainId;

  const deploymentInfo = {
    network,
    chainId: chainId.toString(),
    contractAddress: address,
    deployer: deployer.address,
    name,
    symbol,
    maxSupply,
    baseTokenURI,
    contractURI,
    royaltyReceiver,
    royaltyBps,
    deployedAt: new Date().toISOString(),
  };

  const outDir = path.join(__dirname, "..", "output");
  fs.mkdirSync(outDir, { recursive: true });
  const deploymentPath = path.join(outDir, `deployment-${network}.json`);
  fs.writeFileSync(deploymentPath, JSON.stringify(deploymentInfo, null, 2));
  console.log("Deployment info saved to:", deploymentPath);

  // ── Verification hint ─────────────────────────────────────────────
  console.log("\nTo verify on Basescan, run:");
  console.log(
    `  npx hardhat verify --network ${network} ${address} ` +
      `"${name}" "${symbol}" ${maxSupply} "${baseTokenURI}" "${royaltyReceiver}" ${royaltyBps} "${contractURI}"`
  );
}

main().catch((err) => {
  console.error(err);
  process.exitCode = 1;
});
