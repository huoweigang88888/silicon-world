/**
 * 硅基世界简单部署脚本
 * 部署现有合约到 Sepolia
 */

async function main() {
  console.log("=".repeat(60));
  console.log("硅基世界 Sepolia 部署");
  console.log("=".repeat(60));
  
  const [deployer] = await ethers.getSigners();
  console.log(`网络：sepolia`);
  console.log(`部署者：${deployer.address}`);
  
  // 检查余额
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log(`余额：${ethers.utils.formatEther(balance)} ETH`);
  console.log();
  
  if (balance.eq(0)) {
    console.log("❌ 余额不足！请从水龙头获取 Sepolia ETH");
    console.log("水龙头：https://sepoliafaucet.com/");
    return;
  }
  
  const deploymentInfo = {
    network: "sepolia",
    timestamp: new Date().toISOString(),
    deployer: deployer.address,
    contracts: {}
  };
  
  try {
    // 1. 部署 NFT 合约
    console.log("[1/2] 部署 SiliconWorldNFT 合约...");
    const NFTFactory = await ethers.getContractFactory("SiliconWorldNFT");
    const nft = await NFTFactory.deploy();
    await nft.deployed();
    console.log(`  ✅ NFT 合约：${nft.address}`);
    deploymentInfo.contracts.nft = {
      address: nft.address,
      name: "SiliconWorldNFT"
    };
    
    // 2. 部署市场合约
    console.log("\n[2/2] 部署 Marketplace 合约...");
    const MarketFactory = await ethers.getContractFactory("Marketplace");
    const market = await MarketFactory.deploy();
    await market.deployed();
    console.log(`  ✅ 市场合约：${market.address}`);
    deploymentInfo.contracts.marketplace = {
      address: market.address,
      name: "Marketplace"
    };
    
    // 保存部署信息
    const fs = require("fs");
    const path = require("path");
    const outputPath = path.join(__dirname, "..", "deployments", "sepolia-latest.json");
    
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, JSON.stringify(deploymentInfo, null, 2));
    
    console.log("\n" + "=".repeat(60));
    console.log("✅ 部署完成！");
    console.log("=".repeat(60));
    console.log("\n合约地址:");
    console.log(`  NFT:        ${deploymentInfo.contracts.nft.address}`);
    console.log(`  Marketplace:${deploymentInfo.contracts.marketplace.address}`);
    console.log(`\n部署信息已保存到：${outputPath}`);
    console.log("\n下一步:");
    console.log("  1. 在 Etherscan 验证合约");
    console.log("  2. 更新前端合约地址");
    console.log("  3. 测试合约功能");
    
  } catch (error) {
    console.error("\n❌ 部署失败:", error.message);
    console.error("\n请检查:");
    console.error("  1. 合约是否已编译 (npx hardhat compile)");
    console.error("  2. .env 配置是否正确");
    console.error("  3. 账户是否有足够的 ETH");
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
