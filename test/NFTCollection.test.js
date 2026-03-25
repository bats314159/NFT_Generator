/**
 * test/NFTCollection.test.js – Hardhat unit tests for NFTCollection.sol
 *
 * Run with:  npx hardhat test
 *        or: npm test
 */

const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("NFTCollection", function () {
  // ── Fixtures ────────────────────────────────────────────────────────────────

  /**
   * Deploy a fresh NFTCollection before each test.
   * Returns the contract and the owner / other signers.
   */
  async function deployFixture() {
    const [owner, addr1, addr2] = await ethers.getSigners();

    const NFTCollection = await ethers.getContractFactory("NFTCollection");
    const contract = await NFTCollection.deploy(
      "My NFT Collection",       // name
      "MNC",                     // symbol
      10,                        // maxSupply
      "ipfs://QmBase/",          // baseTokenURI
      owner.address,             // royaltyReceiver
      500,                       // royaltyBps  (5 %)
      "ipfs://QmContract"        // contractURI
    );
    await contract.waitForDeployment();

    return { contract, owner, addr1, addr2 };
  }

  // ── Deployment ───────────────────────────────────────────────────────────────

  describe("Deployment", function () {
    it("sets name and symbol", async function () {
      const { contract } = await deployFixture();
      expect(await contract.name()).to.equal("My NFT Collection");
      expect(await contract.symbol()).to.equal("MNC");
    });

    it("sets MAX_SUPPLY", async function () {
      const { contract } = await deployFixture();
      expect(await contract.MAX_SUPPLY()).to.equal(10);
    });

    it("sets baseURI", async function () {
      const { contract } = await deployFixture();
      expect(await contract.baseURI()).to.equal("ipfs://QmBase/");
    });

    it("sets contractURI", async function () {
      const { contract } = await deployFixture();
      expect(await contract.contractURI()).to.equal("ipfs://QmContract");
    });

    it("sets owner to deployer", async function () {
      const { contract, owner } = await deployFixture();
      expect(await contract.owner()).to.equal(owner.address);
    });

    it("reverts when maxSupply is 0", async function () {
      const [owner] = await ethers.getSigners();
      const NFTCollection = await ethers.getContractFactory("NFTCollection");
      await expect(
        NFTCollection.deploy("X", "X", 0, "", owner.address, 0, "")
      ).to.be.revertedWith("NFTCollection: max supply must be > 0");
    });

    it("reverts when royalty bps > 10 000", async function () {
      const [owner] = await ethers.getSigners();
      const NFTCollection = await ethers.getContractFactory("NFTCollection");
      await expect(
        NFTCollection.deploy("X", "X", 1, "", owner.address, 10001, "")
      ).to.be.revertedWith("NFTCollection: royalty bps must be <= 10000");
    });

    it("reverts when royalty receiver is zero address", async function () {
      const NFTCollection = await ethers.getContractFactory("NFTCollection");
      await expect(
        NFTCollection.deploy(
          "X", "X", 1, "", ethers.ZeroAddress, 500, ""
        )
      ).to.be.revertedWith("NFTCollection: zero royalty receiver");
    });
  });

  // ── Minting ──────────────────────────────────────────────────────────────────

  describe("mint", function () {
    it("owner can mint tokens", async function () {
      const { contract, owner, addr1 } = await deployFixture();
      await contract.mint(addr1.address, 3);
      expect(await contract.totalSupply()).to.equal(3);
      expect(await contract.ownerOf(1)).to.equal(addr1.address);
      expect(await contract.ownerOf(3)).to.equal(addr1.address);
    });

    it("non-owner cannot mint", async function () {
      const { contract, addr1 } = await deployFixture();
      await expect(
        contract.connect(addr1).mint(addr1.address, 1)
      ).to.be.revertedWithCustomError(contract, "OwnableUnauthorizedAccount");
    });

    it("reverts when minting would exceed MAX_SUPPLY", async function () {
      const { contract, owner } = await deployFixture();
      await contract.mint(owner.address, 10);
      await expect(
        contract.mint(owner.address, 1)
      ).to.be.revertedWith("NFTCollection: would exceed max supply");
    });

    it("reverts when minting to zero address", async function () {
      const { contract } = await deployFixture();
      await expect(
        contract.mint(ethers.ZeroAddress, 1)
      ).to.be.revertedWith("NFTCollection: mint to zero address");
    });
  });

  // ── Metadata ─────────────────────────────────────────────────────────────────

  describe("tokenURI", function () {
    it("returns baseURI + tokenId + .json", async function () {
      const { contract, owner } = await deployFixture();
      await contract.mint(owner.address, 1);
      expect(await contract.tokenURI(1)).to.equal("ipfs://QmBase/1.json");
    });

    it("reverts for unminted token", async function () {
      const { contract } = await deployFixture();
      await expect(contract.tokenURI(999)).to.be.reverted;
    });
  });

  describe("setBaseURI", function () {
    it("owner can update baseURI", async function () {
      const { contract } = await deployFixture();
      await contract.setBaseURI("ipfs://QmNewBase/");
      expect(await contract.baseURI()).to.equal("ipfs://QmNewBase/");
    });

    it("emits BaseURIUpdated", async function () {
      const { contract } = await deployFixture();
      await expect(contract.setBaseURI("ipfs://QmNew/"))
        .to.emit(contract, "BaseURIUpdated")
        .withArgs("ipfs://QmNew/");
    });

    it("non-owner cannot update baseURI", async function () {
      const { contract, addr1 } = await deployFixture();
      await expect(
        contract.connect(addr1).setBaseURI("ipfs://evil/")
      ).to.be.revertedWithCustomError(contract, "OwnableUnauthorizedAccount");
    });
  });

  // ── contractURI ───────────────────────────────────────────────────────────────

  describe("contractURI", function () {
    it("returns the contract URI set at construction", async function () {
      const { contract } = await deployFixture();
      expect(await contract.contractURI()).to.equal("ipfs://QmContract");
    });

    it("owner can update contractURI", async function () {
      const { contract } = await deployFixture();
      await contract.setContractURI("ipfs://QmNewContract");
      expect(await contract.contractURI()).to.equal("ipfs://QmNewContract");
    });

    it("emits ContractURIUpdated", async function () {
      const { contract } = await deployFixture();
      await expect(contract.setContractURI("ipfs://QmUpdated"))
        .to.emit(contract, "ContractURIUpdated")
        .withArgs("ipfs://QmUpdated");
    });

    it("non-owner cannot update contractURI", async function () {
      const { contract, addr1 } = await deployFixture();
      await expect(
        contract.connect(addr1).setContractURI("ipfs://evil")
      ).to.be.revertedWithCustomError(contract, "OwnableUnauthorizedAccount");
    });

    it("allows empty contractURI at construction", async function () {
      const [owner] = await ethers.getSigners();
      const NFTCollection = await ethers.getContractFactory("NFTCollection");
      const contract = await NFTCollection.deploy(
        "X", "X", 1, "ipfs://x/", owner.address, 0, ""
      );
      expect(await contract.contractURI()).to.equal("");
    });
  });

  // ── EIP-2981 Royalties ────────────────────────────────────────────────────────

  describe("royaltyInfo", function () {
    it("returns correct royalty amount for 5 %", async function () {
      const { contract, owner } = await deployFixture();
      const [receiver, amount] = await contract.royaltyInfo(1, 10000);
      expect(receiver).to.equal(owner.address);
      expect(amount).to.equal(500); // 5 % of 10 000
    });

    it("owner can update royalty settings", async function () {
      const { contract, addr1 } = await deployFixture();
      await contract.setRoyalty(addr1.address, 1000);
      const [receiver, amount] = await contract.royaltyInfo(1, 10000);
      expect(receiver).to.equal(addr1.address);
      expect(amount).to.equal(1000); // 10 %
    });
  });

  // ── ERC-165 ──────────────────────────────────────────────────────────────────

  describe("supportsInterface", function () {
    it("supports ERC-721 interface", async function () {
      const { contract } = await deployFixture();
      expect(await contract.supportsInterface("0x80ac58cd")).to.be.true;
    });

    it("supports EIP-2981 interface", async function () {
      const { contract } = await deployFixture();
      expect(await contract.supportsInterface("0x2a55205a")).to.be.true;
    });
  });

  // ── Withdraw ─────────────────────────────────────────────────────────────────

  describe("withdraw", function () {
    it("reverts when balance is zero", async function () {
      const { contract } = await deployFixture();
      await expect(contract.withdraw()).to.be.revertedWith(
        "NFTCollection: nothing to withdraw"
      );
    });
  });
});
