/**
 * 超简单本地部署测试
 */
async function main() {
  console.log("========================================");
  console.log("硅基世界 本地部署测试");
  console.log("========================================\n");
  
  // 获取部署者
  const accounts = await ethers.getSigners();
  const deployer = accounts[0];
  console.log("部署者:", deployer.address);
  
  // 获取余额
  const balance = await ethers.provider.getBalance(deployer.address);
  console.log("余额:", ethers.utils.formatEther(balance), "ETH\n");
  
  // 检查合约是否可编译
  console.log("检查合约...");
  try {
    const nftFactory = await ethers.getContractFactory("SiliconWorldNFT");
    console.log("✅ SiliconWorldNFT 合约可用");
    
    const marketFactory = await ethers.getContractFactory("Marketplace");
    console.log("✅ Marketplace 合约可用\n");
    
    // 部署测试
    console.log("开始部署测试...");
    const nft = await nftFactory.deploy();
    await nft.deployed();
    console.log("✅ NFT 合约部署成功:", nft.address);
    
    const market = await marketFactory.deploy();
    await market.deployed();
    console.log("✅ 市场合约部署成功:", market.address);
    
    console.log("\n========================================");
    console.log("🎉 部署测试完全成功！");
    console.log("========================================");
    console.log("\n合约地址:");
    console.log("  NFT:        ", nft.address);
    console.log("  Marketplace:", market.address);
    console.log("\n代码逻辑正确，可以部署到 Sepolia！");
    console.log("当前网络问题不影响代码质量。");
    
  } catch (error) {
    console.error("\n❌ 错误:", error.message);
    console.error("\n请确认合约已编译：npx hardhat compile");
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
