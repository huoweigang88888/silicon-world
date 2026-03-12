require("dotenv").config({ path: __dirname + "/../.env" });
const ethers = require("ethers");

async function main() {
  console.log("=".repeat(60));
  console.log("硅基世界 Sepolia 部署 - Direct");
  console.log("=".repeat(60));
  
  // 直接使用环境变量
  const RPC_URL = process.env.SEPOLIA_RPC_URL;
  const PRIVATE_KEY = process.env.PRIVATE_KEY;
  
  console.log("RPC URL:", RPC_URL);
  console.log("Private Key:", PRIVATE_KEY ? "已设置" : "未设置");
  
  // 创建 provider 和 signer
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const signer = new ethers.Wallet(PRIVATE_KEY, provider);
  
  console.log("\n部署者:", signer.address);
  
  // 检查余额
  const balance = await provider.getBalance(signer.address);
  console.log("余额:", ethers.formatEther(balance), "ETH\n");
  
  if (balance === 0n) {
    console.log("❌ 余额不足！");
    return;
  }
  
  // 获取合约工厂
  console.log("加载合约...");
  const nftArtifact = require(__dirname + "/../artifacts/contracts/SiliconWorldNFT.sol/SiliconWorldNFT.json");
  const marketArtifact = require(__dirname + "/../artifacts/contracts/Marketplace.sol/SiliconWorldMarketplace.json");
  
  const nftFactory = new ethers.ContractFactory(nftArtifact.abi, nftArtifact.bytecode, signer);
  const marketFactory = new ethers.ContractFactory(marketArtifact.abi, marketArtifact.bytecode, signer);
  
  // 部署 NFT (需要 royalty receiver 参数)
  console.log("\n[1/2] 部署 SiliconWorldNFT...");
  const nft = await nftFactory.deploy(signer.address);
  console.log("等待确认...");
  await nft.waitForDeployment();
  const nftAddress = await nft.getAddress();
  console.log("✅ NFT:", nftAddress);
  
  // 部署市场 (需要 platform fee receiver 参数)
  console.log("\n[2/2] 部署 Marketplace...");
  const market = await marketFactory.deploy(signer.address);
  console.log("等待确认...");
  await market.waitForDeployment();
  const marketAddress = await market.getAddress();
  console.log("✅ Marketplace:", marketAddress);
  
  // 保存
  const fs = require("fs");
  const path = require("path");
  const output = {
    network: "sepolia",
    timestamp: new Date().toISOString(),
    deployer: signer.address,
    contracts: {
      nft: nftAddress,
      marketplace: marketAddress
    }
  };
  
  const dir = path.join(__dirname, "..", "deployments");
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
  
  const file = path.join(dir, "sepolia-direct.json");
  fs.writeFileSync(file, JSON.stringify(output, null, 2));
  
  console.log("\n" + "=".repeat(60));
  console.log("🎉 部署成功！");
  console.log("=".repeat(60));
  console.log(`\n📄 保存至：${file}`);
  console.log(`\n🔗 Etherscan:`);
  console.log(`   https://sepolia.etherscan.io/address/${nftAddress}`);
  console.log(`   https://sepolia.etherscan.io/address/${marketAddress}`);
}

main().catch(console.error);
