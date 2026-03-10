// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title SiliconWorldNFT
 * @dev 硅基世界 NFT 合约 (ERC-721)
 */
contract SiliconWorldNFT is ERC721, ERC721URIStorage, Ownable {
    uint256 private _tokenIdCounter;

    uint256 public royaltyBps = 500; // 5%
    address public royaltyReceiver;

    struct NFTInfo {
        uint256 tokenId;
        address creator;
        string nftType;
        uint256 createdAt;
        bool exists;
    }

    mapping(uint256 => NFTInfo) public nftInfo;

    event NFTMinted(
        uint256 indexed tokenId,
        address indexed creator,
        address indexed owner,
        string nftType,
        string tokenURI
    );

    constructor(address _royaltyReceiver) 
        ERC721("SiliconWorld", "SWNFT")
    {
        royaltyReceiver = _royaltyReceiver;
        _transferOwnership(msg.sender);
    }

    function mint(
        address to,
        string memory _tokenURI,
        string memory nftType
    ) public onlyOwner returns (uint256) {
        _tokenIdCounter++;
        uint256 tokenId = _tokenIdCounter;

        _safeMint(to, tokenId);
        _setTokenURI(tokenId, _tokenURI);

        nftInfo[tokenId] = NFTInfo({
            tokenId: tokenId,
            creator: msg.sender,
            nftType: nftType,
            createdAt: block.timestamp,
            exists: true
        });

        emit NFTMinted(tokenId, msg.sender, to, nftType, _tokenURI);

        return tokenId;
    }

    function mintBatch(
        address to,
        string[] memory _tokenURIs,
        string[] memory nftTypes
    ) public onlyOwner returns (uint256[] memory) {
        require(_tokenURIs.length == nftTypes.length, "Arrays length mismatch");
        
        uint256[] memory tokenIds = new uint256[](_tokenURIs.length);
        
        for (uint256 i = 0; i < _tokenURIs.length; i++) {
            tokenIds[i] = mint(to, _tokenURIs[i], nftTypes[i]);
        }

        return tokenIds;
    }

    function getNFTInfo(uint256 tokenId) public view returns (NFTInfo memory) {
        require(ownerOf(tokenId) != address(0), "NFT does not exist");
        return nftInfo[tokenId];
    }

    function totalSupply() public view returns (uint256) {
        return _tokenIdCounter;
    }

    function setRoyaltyBps(uint256 bps) public onlyOwner {
        require(bps <= 1000, "Royalty too high");
        royaltyBps = bps;
    }

    function setRoyaltyReceiver(address receiver) public onlyOwner {
        require(receiver != address(0), "Invalid address");
        royaltyReceiver = receiver;
    }

    function calculateRoyalty(uint256 salePrice) public view returns (uint256) {
        return (salePrice * royaltyBps) / 10000;
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
        nftInfo[tokenId].exists = false;
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
