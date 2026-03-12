require("dotenv").config({ path: __dirname + "/../.env" });

console.log("环境变量检查:");
console.log("SEPOLIA_RPC_URL:", process.env.SEPOLIA_RPC_URL);
console.log("PRIVATE_KEY:", process.env.PRIVATE_KEY ? "已设置" : "未设置");
console.log("\nHardhat 配置检查...");

async function main() {
  const [signer] = await ethers.getSigners();
  console.log("Signer:", signer.address);
  
  const network = await ethers.provider.getNetwork();
  console.log("Network:", network.name, network.chainId);
}

main().catch(console.error);
