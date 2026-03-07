// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title WorldNFT
 * @dev 硅基世界 NFT 合约
 * 
 * 支持:
 * - 虚拟土地
 * - 建筑
 * - 物品
 * - 艺术品
 * - 特殊身份
 */
contract WorldNFT is ERC721, ERC721URIStorage, Ownable {
    uint256 private _nextTokenId;
    
    // NFT 类型
    enum NFTType {
        Land,      // 土地
        Building,  // 建筑
        Item,      // 物品
        Artwork,   // 艺术品
        Identity   // 特殊身份
    }
    
    // NFT 信息
    struct NFTInfo {
        NFTType nftType;
        string name;
        string description;
        uint256 createdAt;
        address creator;
        uint256 properties; // 属性位图
    }
    
    mapping(uint256 => NFTInfo) private _nftInfo;
    
    // 事件
    event NFTCreated(
        uint256 indexed tokenId,
        NFTType indexed nftType,
        address indexed creator,
        string name
    );
    
    constructor() ERC721("SiliconWorld", "SWNFT") Ownable(msg.sender) {
        _nextTokenId = 0;
    }
    
    /**
     * @dev 铸造 NFT
     * @param to 接收地址
     * @param nftType NFT 类型
     * @param name 名称
     * @param description 描述
     * @param uri 元数据 URI
     * @param properties 属性位图
     */
    function mint(
        address to,
        NFTType nftType,
        string memory name,
        string memory description,
        string memory uri,
        uint256 properties
    ) external onlyOwner returns (uint256) {
        uint256 tokenId = _nextTokenId++;
        
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
        
        _nftInfo[tokenId] = NFTInfo({
            nftType: nftType,
            name: name,
            description: description,
            createdAt: block.timestamp,
            creator: msg.sender,
            properties: properties
        });
        
        emit NFTCreated(tokenId, nftType, msg.sender, name);
        
        return tokenId;
    }
    
    /**
     * @dev 获取 NFT 信息
     */
    function getNFTInfo(uint256 tokenId) external view returns (NFTInfo memory) {
        require(_exists(tokenId), "NFT does not exist");
        return _nftInfo[tokenId];
    }
    
    /**
     * @dev 获取 NFT 类型
     */
    function getNFTType(uint256 tokenId) external view returns (NFTType) {
        return _nftInfo[tokenId].nftType;
    }
    
    /**
     * @dev 获取下一个 Token ID
     */
    function getNextTokenId() external view returns (uint256) {
        return _nextTokenId;
    }
    
    /**
     * @dev 获取总供应量
     */
    function totalSupply() external view returns (uint256) {
        return _nextTokenId;
    }
    
    // 重写 required 函数
    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
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
