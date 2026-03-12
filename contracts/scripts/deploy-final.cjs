/**
 * 最终部署脚本 - 硬编码配置
 */
const hre = require("hardhat");

async function main() {
  console.log("=".repeat(60));
  console.log("硅基世界 Sepolia 部署 - 最终尝试");
  console.log("=".repeat(60));
  
  // 硬编码配置（不依赖 .env）
  const RPC_URL = "https://eth-sepolia.g.alchemy.com/v2/AP6EAjqS9hYALHJAFuk1K";
  const PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80";
  
  const { ethers } = hre;
  
  // 创建自定义 provider
  const provider = new ethers.providers.JsonRpcProvider(RPC_URL);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  
  console.log(`网络：sepolia`);
  console.log(`部署者：${wallet.address}`);
  
  // 检查余额
  const balance = await provider.getBalance(wallet.address);
  console.log(`余额：${ethers.utils.formatEther(balance)} ETH`);
  
  if (balance.eq(0)) {
    console.log("\n❌ 余额不足！请从水龙头获取 Sepolia ETH");
    console.log("水龙头：https://sepoliafaucet.com/");
    return;
  }
  
  const deploymentInfo = {
    network: "sepolia",
    timestamp: new Date().toISOString(),
    deployer: wallet.address,
    contracts: {}
  };
  
  try {
    // 获取合约工厂（使用 signer）
    const nftFactory = await ethers.getContractFactory("SiliconWorldNFT", wallet);
    const marketFactory = await ethers.getContractFactory("Marketplace", wallet);
    
    // 部署 NFT
    console.log("\n[1/2] 部署 SiliconWorldNFT...");
    const nft = await nftFactory.deploy();
    console.log("  等待确认...");
    await nft.deployed();
    console.log(`  ✅ NFT: ${nft.address}`);
    deploymentInfo.contracts.nft = nft.address;
    
    // 部署市场
    console.log("\n[2/2] 部署 Marketplace...");
    const market = await marketFactory.deploy();
    console.log("  等待确认...");
    await market.deployed();
    console.log(`  ✅ Marketplace: ${market.address}`);
    deploymentInfo.contracts.marketplace = market.address;
    
    // 保存部署信息
    const fs = require("fs");
    const path = require("path");
    const outputPath = path.join(__dirname, "..", "deployments", "sepolia-final.json");
    
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, JSON.stringify(deploymentInfo, null, 2));
    
    console.log("\n" + "=".repeat(60));
    console.log("🎉 部署成功！");
    console.log("=".repeat(60));
    console.log("\n合约地址:");
    console.log(`  NFT:         ${deploymentInfo.contracts.nft.address}`);
    console.log(`  Marketplace: ${deploymentInfo.contracts.marketplace.address}`);
    console.log(`\n部署信息：deployments/sepolia-final.json`);
    console.log(`\nEtherscan 查看:`);
    console.log(`  https://sepolia.etherscan.io/address/${deploymentInfo.contracts.nft.address}`);
    console.log(`  https://sepolia.etherscan.io/address/${deploymentInfo.contracts.marketplace.address}`);
    
  } catch (error) {
    console.error("\n❌ 部署失败:", error.message);
    if (error.message.includes("insufficient funds")) {
      console.error("\n提示：账户余额不足，请获取测试 ETH");
    } else if (error.message.includes("nonce")) {
      console.error("\n提示：nonce 问题，请重试");
    }
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
