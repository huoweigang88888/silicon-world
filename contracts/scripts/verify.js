import hre from "hardhat";

async function main() {
    console.log("🔍 开始验证合约...");

    // 从部署信息文件读取合约地址
    const fs = require("fs");
    const path = require("path");
    
    const deploymentPath = path.join(__dirname, "../deployment-info.json");
    
    if (!fs.existsSync(deploymentPath)) {
        console.error("❌ 部署信息文件不存在，请先运行部署脚本");
        return;
    }
    
    const deploymentInfo = JSON.parse(fs.readFileSync(deploymentPath, "utf8"));
    
    console.log("📊 部署信息:");
    console.log("  网络:", deploymentInfo.network);
    console.log("  部署者:", deploymentInfo.deployer);
    console.log("  时间:", deploymentInfo.timestamp);
    console.log("");
    
    const nftAddress = deploymentInfo.contracts.SiliconWorldNFT;
    const marketplaceAddress = deploymentInfo.contracts.SiliconWorldMarketplace;
    
    console.log("📄 合约地址:");
    console.log("  NFT 合约:", nftAddress);
    console.log("  市场合约:", marketplaceAddress);
    console.log("");
    
    // 验证 NFT 合约
    console.log("🔍 验证 SiliconWorldNFT 合约...");
    try {
        await hre.run("verify:verify", {
            address: nftAddress,
            constructorArguments: [
                deploymentInfo.config.royaltyReceiver
            ]
        });
        console.log("✅ NFT 合约验证成功!");
    } catch (error) {
        if (error.message.includes("Already Verified")) {
            console.log("✅ NFT 合约已经验证过");
        } else {
            console.error("❌ NFT 合约验证失败:", error.message);
        }
    }
    
    // 验证市场合约
    console.log("\n🔍 验证 SiliconWorldMarketplace 合约...");
    try {
        await hre.run("verify:verify", {
            address: marketplaceAddress,
            constructorArguments: [
                deploymentInfo.config.platformFeeReceiver
            ]
        });
        console.log("✅ 市场合约验证成功!");
    } catch (error) {
        if (error.message.includes("Already Verified")) {
            console.log("✅ 市场合约已经验证过");
        } else {
            console.error("❌ 市场合约验证失败:", error.message);
        }
    }
    
    console.log("\n" + "=".repeat(60));
    console.log("✅ 合约验证完成!");
    console.log("=".repeat(60));
    console.log("");
    console.log("📝 查看合约:");
    console.log(`  NFT 合约：https://${deploymentInfo.network}.etherscan.io/address/${nftAddress}#code`);
    console.log(`  市场合约：https://${deploymentInfo.network}.etherscan.io/address/${marketplaceAddress}#code`);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
