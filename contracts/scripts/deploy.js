import hre from "hardhat";
import fs from "fs";

async function main() {
  console.log("🚀 开始部署硅基世界智能合约...");

  // 获取部署者地址
  const [deployer] = await hre.ethers.getSigners();
  console.log("📝 部署者地址:", deployer.address);

  // 获取余额
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("💰 账户余额:", hre.ethers.formatEther(balance), "ETH");

  // 部署参数
  const royaltyReceiver = deployer.address; // 版税接收地址
  const platformFeeReceiver = deployer.address; // 平台费用接收地址

  // 1. 部署 NFT 合约
  console.log("\n📦 部署 SiliconWorldNFT 合约...");
  const NFTFactory = await hre.ethers.getContractFactory("SiliconWorldNFT");
  const nftContract = await NFTFactory.deploy(royaltyReceiver);
  await nftContract.waitForDeployment();
  const nftAddress = await nftContract.getAddress();
  console.log("✅ SiliconWorldNFT 部署成功:", nftAddress);

  // 2. 部署市场合约
  console.log("\n🏪 部署 SiliconWorldMarketplace 合约...");
  const MarketplaceFactory = await hre.ethers.getContractFactory("SiliconWorldMarketplace");
  const marketplaceContract = await MarketplaceFactory.deploy(platformFeeReceiver);
  await marketplaceContract.waitForDeployment();
  const marketplaceAddress = await marketplaceContract.getAddress();
  console.log("✅ SiliconWorldMarketplace 部署成功:", marketplaceAddress);

  // 3. 输出部署信息
  console.log("\n" + "=".repeat(60));
  console.log("📊 部署完成！");
  console.log("=".repeat(60));
  console.log("网络:", hre.network.name);
  console.log("部署者:", deployer.address);
  console.log("");
  console.log("📄 合约地址:");
  console.log("  SiliconWorldNFT:        ", nftAddress);
  console.log("  SiliconWorldMarketplace:", marketplaceAddress);
  console.log("");
  console.log("⚙️  配置信息:");
  console.log("  版税比例：5%");
  console.log("  平台手续费：1%");
  console.log("  版税接收地址:", royaltyReceiver);
  console.log("  平台费用地址:", platformFeeReceiver);
  console.log("=".repeat(60));

  // 4. 保存部署信息
  const deploymentInfo = {
    network: hre.network.name,
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    contracts: {
      SiliconWorldNFT: nftAddress,
      SiliconWorldMarketplace: marketplaceAddress
    },
    config: {
      royaltyBps: 500, // 5%
      platformFeeBps: 100, // 1%
      royaltyReceiver: royaltyReceiver,
      platformFeeReceiver: platformFeeReceiver
    }
  };

  const outputPath = "./deployment-info.json";
  fs.writeFileSync(outputPath, JSON.stringify(deploymentInfo, null, 2));
  console.log(`\n💾 部署信息已保存到：${outputPath}`);

  // 5. 验证合约 (如果在公共网络)
  if (hre.network.name !== "hardhat") {
    console.log("\n⏳ 等待合约验证...");
    console.log("提示：使用以下命令验证合约:");
    console.log(`  npx hardhat verify --network ${hre.network.name} ${nftAddress} ${deployer.address} ${royaltyReceiver}`);
    console.log(`  npx hardhat verify --network ${hre.network.name} ${marketplaceAddress} ${deployer.address} ${platformFeeReceiver}`);
  }
}

// 执行部署
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
