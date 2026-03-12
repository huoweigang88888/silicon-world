#!/usr/bin/env node

/**
 * 硅基世界测试网部署脚本
 * 
 * 功能:
 * 1. 部署智能合约到 Goerli
 * 2. 验证合约源码
 * 3. 初始化合约状态
 * 4. 配置后端服务
 */

const { ethers } = require("hardhat");
const fs = require("fs");
const path = require("path");

// 部署配置 (initialSupply 在 main 函数中设置)
const CONFIG = {
  network: "sepolia",  // 更新为 Sepolia (Goerli 已废弃)
  tokenName: "Silicon World Token",
  tokenSymbol: "SWT",
};

// 部署结果存储
const deploymentInfo = {
  network: CONFIG.network,
  timestamp: new Date().toISOString(),
  contracts: {},
};

async function main() {
  console.log("=".repeat(60));
  console.log("硅基世界测试网部署");
  console.log("=".repeat(60));
  console.log(`网络：${CONFIG.network}`);
  console.log(`部署者：${(await ethers.getSigners())[0].address}`);
  console.log();

  // 设置初始供应量
  CONFIG.initialSupply = ethers.utils.parseEther("1000000"); // 100 万代币

  // 1. 部署代币合约
  console.log("[1/4] 部署代币合约...");
  const TokenContract = await ethers.getContractFactory("SiliconWorldToken");
  const token = await TokenContract.deploy(
    CONFIG.initialSupply,
    CONFIG.tokenName,
    CONFIG.tokenSymbol
  );
  await token.deployed();
  console.log(`  代币合约：${token.address}`);
  deploymentInfo.contracts.token = {
    address: token.address,
    name: CONFIG.tokenName,
    symbol: CONFIG.tokenSymbol,
  };

  // 2. 部署治理合约
  console.log("\n[2/4] 部署治理合约...");
  const GovernanceContract = await ethers.getContractFactory("SiliconGovernance");
  const governance = await GovernanceContract.deploy(token.address);
  await governance.deployed();
  console.log(`  治理合约：${governance.address}`);
  deploymentInfo.contracts.governance = {
    address: governance.address,
  };

  // 3. 部署积分合约
  console.log("\n[3/4] 部署积分合约...");
  const ReputationContract = await ethers.getContractFactory("ReputationSystem");
  const reputation = await ReputationContract.deploy();
  await reputation.deployed();
  console.log(`  积分合约：${reputation.address}`);
  deploymentInfo.contracts.reputation = {
    address: reputation.address,
  };

  // 4. 部署小组合约
  console.log("\n[4/4] 部署小组合约...");
  const GroupsContract = await ethers.getContractFactory("GroupsManager");
  const groups = await GroupsContract.deploy();
  await groups.deployed();
  console.log(`  小组合约：${groups.address}`);
  deploymentInfo.contracts.groups = {
    address: groups.address,
  };

  // 保存部署信息
  const outputPath = path.join(__dirname, "..", "deployments", `${CONFIG.network}-latest.json`);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, JSON.stringify(deploymentInfo, null, 2));
  console.log(`\n部署信息已保存到：${outputPath}`);

  // 打印总结
  console.log();
  console.log("=".repeat(60));
  console.log("部署完成！");
  console.log("=".repeat(60));
  console.log("合约地址:");
  console.log(`  代币 (Token):      ${deploymentInfo.contracts.token.address}`);
  console.log(`  治理 (Governance): ${deploymentInfo.contracts.governance.address}`);
  console.log(`  积分 (Reputation): ${deploymentInfo.contracts.reputation.address}`);
  console.log(`  小组 (Groups):     ${deploymentInfo.contracts.groups.address}`);
  console.log();
  console.log("下一步:");
  console.log("  1. 验证合约：npm run verify:goerli");
  console.log("  2. 添加流动性 (如需)");
  console.log("  3. 配置后端服务");
  console.log("  4. 开始测试");
  console.log();
}

// 执行部署
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
