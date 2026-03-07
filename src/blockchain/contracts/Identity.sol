// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title Identity
 * @dev 去中心化身份管理合约
 */
contract Identity {
    
    // DID 文档结构
    struct DIDDocument {
        string did;
        address controller;
        uint256 created;
        uint256 updated;
        string publicKey;
        bool active;
    }
    
    // DID 映射
    mapping(string => DIDDocument) private _documents;
    
    // 控制器拥有的所有 DID
    mapping(address => string[]) private _controllerDIDs;
    
    // 事件
    event DIDCreated(string indexed did, address indexed controller, uint256 timestamp);
    event DIDUpdated(string indexed did, uint256 timestamp);
    event DIDDeactivated(string indexed did, uint256 timestamp);
    
    /**
     * @dev 创建新的 DID
     * @param did DID 字符串
     * @param publicKey 公钥
     */
    function createDID(string memory did, string memory publicKey) external {
        require(!_documents[did].active, "DID already exists");
        
        DIDDocument storage doc = _documents[did];
        doc.did = did;
        doc.controller = msg.sender;
        doc.created = block.timestamp;
        doc.updated = block.timestamp;
        doc.publicKey = publicKey;
        doc.active = true;
        
        _controllerDIDs[msg.sender] = _controllerDIDs[msg.sender];
        _controllerDIDs[msg.sender].push(did);
        
        emit DIDCreated(did, msg.sender, block.timestamp);
    }
    
    /**
     * @dev 更新 DID 文档
     * @param did DID 字符串
     * @param newPublicKey 新公钥
     */
    function updateDID(string memory did, string memory newPublicKey) external {
        require(_documents[did].active, "DID not active");
        require(_documents[did].controller == msg.sender, "Not controller");
        
        _documents[did].publicKey = newPublicKey;
        _documents[did].updated = block.timestamp;
        
        emit DIDUpdated(did, block.timestamp);
    }
    
    /**
     * @dev 停用 DID
     * @param did DID 字符串
     */
    function deactivateDID(string memory did) external {
        require(_documents[did].active, "DID not active");
        require(_documents[did].controller == msg.sender, "Not controller");
        
        _documents[did].active = false;
        _documents[did].updated = block.timestamp;
        
        emit DIDDeactivated(did, block.timestamp);
    }
    
    /**
     * @dev 获取 DID 文档
     * @param did DID 字符串
     * @return DIDDocument
     */
    function getDID(string memory did) external view returns (
        string memory,
        address,
        uint256,
        uint256,
        string memory,
        bool
    ) {
        DIDDocument storage doc = _documents[did];
        return (
            doc.did,
            doc.controller,
            doc.created,
            doc.updated,
            doc.publicKey,
            doc.active
        );
    }
    
    /**
     * @dev 检查 DID 是否有效
     * @param did DID 字符串
     * @return 是否有效
     */
    function isValid(string memory did) external view returns (bool) {
        return _documents[did].active;
    }
    
    /**
     * @dev 获取控制器拥有的 DID 数量
     * @param controller 控制器地址
     * @return DID 数量
     */
    function getDIDCount(address controller) external view returns (uint256) {
        return _controllerDIDs[controller].length;
    }
    
    /**
     * @dev 获取控制器的 DID 列表
     * @param controller 控制器地址
     * @param offset 偏移量
     * @param limit 限制数量
     * @return DID 列表
     */
    function getControllerDIDs(
        address controller,
        uint256 offset,
        uint256 limit
    ) external view returns (string[] memory) {
        string[] memory allDIDs = _controllerDIDs[controller];
        require(offset < allDIDs.length, "Offset out of bounds");
        
        uint256 end = offset + limit;
        if (end > allDIDs.length) {
            end = allDIDs.length;
        }
        
        uint256 resultLength = end - offset;
        string[] memory result = new string[](resultLength);
        
        for (uint256 i = 0; i < resultLength; i++) {
            result[i] = allDIDs[offset + i];
        }
        
        return result;
    }
}
