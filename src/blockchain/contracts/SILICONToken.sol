// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title SILICONToken
 * @dev 硅基世界原生代币 - ERC20
 * 
 * 代币经济:
 * - 总量：10 亿枚
 * - 初始流通：20%
 * - 挖矿奖励：40% (10 年释放)
 * - 团队储备：20% (4 年线性释放)
 * - 生态基金：20%
 */
contract SILICONToken is ERC20, ERC20Burnable, Ownable {
    // 代币总量
    uint256 private constant _MAX_SUPPLY = 1000000000 * 10^18; // 10 亿枚
    
    // 解锁时间表
    mapping(address => uint256) private _unlockTimes;
    mapping(address => uint256) private _lockedAmounts;
    
    // 事件
    event TokensUnlocked(address indexed beneficiary, uint256 amount);
    event TokensLocked(address indexed beneficiary, uint256 amount, uint256 unlockTime);
    
    constructor() ERC20("SILICON", "SIL") Ownable(msg.sender) {
        // 铸造 10 亿枚
        _mint(msg.sender, _MAX_SUPPLY);
    }
    
    /**
     * @dev 锁定代币
     * @param beneficiary 受益人地址
     * @param amount 锁定数量
     * @param unlockTime 解锁时间戳
     */
    function lockTokens(
        address beneficiary,
        uint256 amount,
        uint256 unlockTime
    ) external onlyOwner {
        require(unlockTime > block.timestamp, "Unlock time must be in future");
        require(amount <= balanceOf(address(this)), "Insufficient tokens");
        
        // 转账到受益人但锁定
        _transfer(address(this), beneficiary, amount);
        _lockedAmounts[beneficiary] += amount;
        _unlockTimes[beneficiary] = unlockTime;
        
        emit TokensLocked(beneficiary, amount, unlockTime);
    }
    
    /**
     * @dev 解锁代币
     */
    function unlockTokens() external {
        require(_unlockTimes[msg.sender] <= block.timestamp, "Tokens still locked");
        require(_lockedAmounts[msg.sender] > 0, "No locked tokens");
        
        uint256 amount = _lockedAmounts[msg.sender];
        _lockedAmounts[msg.sender] = 0;
        _unlockTimes[msg.sender] = 0;
        
        emit TokensUnlocked(msg.sender, amount);
    }
    
    /**
     * @dev 获取锁定信息
     */
    function getLockedInfo(address account) external view returns (
        uint256 lockedAmount,
        uint256 unlockTime
    ) {
        return (_lockedAmounts[account], _unlockTimes[account]);
    }
    
    /**
     * @dev 获取最大供应量
     */
    function maxSupply() external pure returns (uint256) {
        return _MAX_SUPPLY;
    }
    
    /**
     * @dev 重写转账，检查锁定
     */
    function transfer(address to, uint256 amount) public override returns (bool) {
        require(
            amount <= (balanceOf(msg.sender) - _lockedAmounts[msg.sender]),
            "Insufficient unlocked balance"
        );
        return super.transfer(to, amount);
    }
    
    /**
     * @dev 重写授权转账，检查锁定
     */
    function transferFrom(address from, address to, uint256 amount) public override returns (bool) {
        require(
            amount <= (balanceOf(from) - _lockedAmounts[from]),
            "Insufficient unlocked balance"
        );
        return super.transferFrom(from, to, amount);
    }
}
