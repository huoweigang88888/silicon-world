/**
 * 硅基世界本地部署脚本
 * 部署到 Hardhat 本地网络
 */

async function main() {
  console.log("=".repeat(60));
  console.log("硅基世界 本地部署测试");
  console.log("=".repeat(60));
  
  const [deployer] = await ethers.getSigners();
  console.log(`部署者：${deployer.address}`);
  
  const balance = await deployer.getBalance();
  console.log(`余额：${ethers.utils.formatEther(balance)} ETH`);
  console.log();
  
  const deploymentInfo = {
    network: "localhost",
    timestamp: new Date().toISOString(),
    deployer: deployer.address,
    contracts: {}
  };
  
  try {
    // 部署 NFT 合约
    console.log("[1/2] 部署 SiliconWorldNFT 合约...");
    const NFTFactory = await ethers.getContractFactory("SiliconWorldNFT");
    const nft = await NFTFactory.deploy();
    await nft.deployed();
    console.log(`  ✅ NFT: ${nft.address}`);
    deploymentInfo.contracts.nft = nft.address;
    
    // 部署市场合约
    console.log("[2/2] 部署 Marketplace 合约...");
    const MarketFactory = await ethers.getContractFactory("Marketplace");
    const market = await MarketFactory.deploy();
    await market.deployed();
    console.log(`  ✅ Marketplace: ${market.address}`);
    deploymentInfo.contracts.marketplace = market.address;
    
    // 保存部署信息
    const fs = require("fs");
    const path = require("path");
    const outputPath = path.join(__dirname, "..", "deployments", "localhost-latest.json");
    
    fs.mkdirSync(path.dirname(outputPath), { recursive: true });
    fs.writeFileSync(outputPath, JSON.stringify(deploymentInfo, null, 2));
    
    console.log("\n" + "=".repeat(60));
    console.log("✅ 本地部署成功！");
    console.log("=".repeat(60));
    console.log(`\n合约地址已保存到：deployments/localhost-latest.json`);
    console.log("\n⚠️  注意：这是本地测试网络，重启后合约会消失");
    console.log("   部署到 Sepolia 需要解决网络连接问题\n");
    
  } catch (error) {
    console.error("\n❌ 部署失败:", error.message);
    if (error.message.includes("no provider")) {
      console.error("\n提示：请先在另一个终端运行：npx hardhat node");
    }
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
