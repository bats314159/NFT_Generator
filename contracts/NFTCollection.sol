// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/interfaces/IERC2981.sol";

/**
 * @title NFTCollection
 * @notice ERC-721 collection with on-chain royalties (EIP-2981), a
 *         configurable base URI, and a hard cap on supply.  Deployed on
 *         Base (chain ID 8453) but compatible with any EVM network.
 *
 * Key features
 * ─────────────
 * • Owner-only minting up to MAX_SUPPLY
 * • Configurable per-token metadata URI (baseURI + tokenId + ".json")
 * • EIP-2981 royalty support (e.g. marketplaces like OpenSea)
 * • setBaseURI() lets the owner point tokens at a new IPFS CID after
 *   the collection has been deployed (useful during reveal workflows)
 * • Withdraw function so ETH sent to the contract can be recovered
 */
contract NFTCollection is ERC721URIStorage, Ownable, IERC2981 {
    using Strings for uint256;

    // ── Collection constants ──────────────────────────────────────────
    uint256 public immutable MAX_SUPPLY;

    // ── State ─────────────────────────────────────────────────────────
    uint256 private _nextTokenId;
    string  private _baseTokenURI;

    // EIP-2981 royalty
    address private _royaltyReceiver;
    uint96  private _royaltyBps; // basis points, e.g. 500 = 5 %

    // ── Events ────────────────────────────────────────────────────────
    event BaseURIUpdated(string newBaseURI);
    event RoyaltyUpdated(address receiver, uint96 bps);

    // ── Constructor ───────────────────────────────────────────────────
    /**
     * @param name_           Human-readable collection name
     * @param symbol_         Token symbol (e.g. "MNC")
     * @param maxSupply_      Hard cap on total tokens that can ever be minted
     * @param baseTokenURI_   IPFS URI of the metadata folder (trailing slash),
     *                        e.g. "ipfs://Qm…abc/"
     * @param royaltyReceiver Address that receives secondary-sale royalties
     * @param royaltyBps_     Royalty in basis points (100 bps = 1 %)
     */
    constructor(
        string memory name_,
        string memory symbol_,
        uint256 maxSupply_,
        string memory baseTokenURI_,
        address royaltyReceiver,
        uint96  royaltyBps_
    ) ERC721(name_, symbol_) Ownable(msg.sender) {
        require(maxSupply_ > 0,        "NFTCollection: max supply must be > 0");
        require(royaltyBps_ <= 10_000, "NFTCollection: royalty bps must be <= 10000");
        require(royaltyReceiver != address(0), "NFTCollection: zero royalty receiver");

        MAX_SUPPLY       = maxSupply_;
        _baseTokenURI    = baseTokenURI_;
        _royaltyReceiver = royaltyReceiver;
        _royaltyBps      = royaltyBps_;
        _nextTokenId     = 1;
    }

    // ── Minting ───────────────────────────────────────────────────────

    /**
     * @notice Mint *quantity* tokens to *to*.  Only callable by the owner.
     */
    function mint(address to, uint256 quantity) external onlyOwner {
        require(to != address(0), "NFTCollection: mint to zero address");
        require(
            _nextTokenId + quantity - 1 <= MAX_SUPPLY,
            "NFTCollection: would exceed max supply"
        );

        for (uint256 i = 0; i < quantity; ++i) {
            uint256 tokenId = _nextTokenId++;
            _safeMint(to, tokenId);
        }
    }

    // ── Metadata ──────────────────────────────────────────────────────

    /**
     * @notice Update the base URI (e.g. after IPFS upload completes).
     */
    function setBaseURI(string calldata newBaseURI) external onlyOwner {
        _baseTokenURI = newBaseURI;
        emit BaseURIUpdated(newBaseURI);
    }

    /**
     * @dev Returns ``<baseURI><tokenId>.json`` for each token.
     */
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721URIStorage)
        returns (string memory)
    {
        _requireOwned(tokenId);
        // If a per-token URI was set explicitly, prefer it
        string memory perToken = super.tokenURI(tokenId);
        if (bytes(perToken).length > 0) {
            return perToken;
        }
        return string(abi.encodePacked(_baseTokenURI, tokenId.toString(), ".json"));
    }

    function baseURI() external view returns (string memory) {
        return _baseTokenURI;
    }

    // ── Supply helpers ────────────────────────────────────────────────

    /** @notice Total number of tokens minted so far. */
    function totalSupply() external view returns (uint256) {
        return _nextTokenId - 1;
    }

    // ── EIP-2981 Royalty ─────────────────────────────────────────────

    /**
     * @inheritdoc IERC2981
     */
    function royaltyInfo(uint256 /*tokenId*/, uint256 salePrice)
        external
        view
        override
        returns (address receiver, uint256 royaltyAmount)
    {
        receiver = _royaltyReceiver;
        royaltyAmount = (salePrice * _royaltyBps) / 10_000;
    }

    /**
     * @notice Update royalty settings.  Only callable by the owner.
     */
    function setRoyalty(address receiver, uint96 bps) external onlyOwner {
        require(bps <= 10_000,            "NFTCollection: bps must be <= 10000");
        require(receiver != address(0),   "NFTCollection: zero royalty receiver");
        _royaltyReceiver = receiver;
        _royaltyBps      = bps;
        emit RoyaltyUpdated(receiver, bps);
    }

    // ── ERC-165 ───────────────────────────────────────────────────────

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721URIStorage, IERC165)
        returns (bool)
    {
        return
            interfaceId == type(IERC2981).interfaceId ||
            super.supportsInterface(interfaceId);
    }

    // ── Financials ────────────────────────────────────────────────────

    /** @notice Withdraw any ETH accidentally sent to the contract. */
    function withdraw() external onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "NFTCollection: nothing to withdraw");
        (bool ok, ) = payable(owner()).call{value: balance}("");
        require(ok, "NFTCollection: withdraw failed");
    }

    receive() external payable {}
}
