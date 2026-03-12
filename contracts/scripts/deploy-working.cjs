async function main() {
  console.log("=".repeat(60));
  console.log("硅基世界 Sepolia 部署");
  console.log("=".repeat(60));
  
  const [deployer] = await ethers.getSigners();
  console.log(`部署者：${deployer.address}`);
  
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log(`余额：${ethers.utils.formatEther(balance)} ETH\n`);
  
  if (balance.eq(0)) {
    console.log("❌ 余额不足！");
    return;
  }
  
  console.log("开始部署...\n");
  
  // 部署 NFT 合约
  console.log("[1/2] SiliconWorldNFT...");
  const NFT = await ethers.getContractFactory("SiliconWorldNFT");
  const nft = await NFT.deploy();
  await nft.deployed();
  console.log(`✅ ${nft.address}\n`);
  
  // 部署市场合约
  console.log("[2/2] Marketplace...");
  const Market = await ethers.getContractFactory("Marketplace");
  const market = await Market.deploy();
  await market.deployed();
  console.log(`✅ ${market.address}\n`);
  
  // 保存
  const fs = require("fs");
  const path = require("path");
  const output = {
    network: "sepolia",
    timestamp: new Date().toISOString(),
    deployer: deployer.address,
    contracts: {
      nft: nft.address,
      marketplace: market.address
    }
  };
  
  const dir = path.join(__dirname, "..", "deployments");
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  
  const file = path.join(dir, "sepolia.json");
  fs.writeFileSync(file, JSON.stringify(output, null, 2));
  
  console.log("=".repeat(60));
  console.log("🎉 部署成功！");
  console.log("=".repeat(60));
  console.log(`\n📄 保存至：${file}`);
  console.log(`\n🔗 Etherscan:`);
  console.log(`   https://sepolia.etherscan.io/address/${nft.address}`);
  console.log(`   https://sepolia.etherscan.io/address/${market.address}`);
}

main().catch(console.error).finally(() => process.exit(0));
