#!/usr/bin/env python3
"""
NFT 铸造演示脚本

演示完整的 NFT 铸造流程：
1. 连接钱包
2. 准备元数据
3. 调用合约铸造
4. 查看结果
"""

import json
from datetime import datetime

def print_header(title):
    print("\n" + "="*60)
    print("  " + title)
    print("="*60 + "\n")

def create_nft_metadata(nft_type, name, description, attributes=None):
    """创建 NFT 元数据"""
    
    metadata = {
        "name": name,
        "description": description,
        "type": nft_type,
        "attributes": attributes or [],
        "created_at": datetime.utcnow().isoformat(),
        "creator": "Silicon World"
    }
    
    return metadata

def demo_mint_flow():
    """演示铸造流程"""
    
    print_header("[NFT 铸造演示]")
    
    # 1. 准备 NFT 数据
    print("1️⃣ 准备 NFT 数据...")
    
    nft_examples = [
        {
            "type": "land",
            "name": "中心城地块 #001",
            "description": "位于硅基世界中心城的珍贵地块，坐标 (100, 200)，面积 1000 平方米。",
            "attributes": [
                {"trait_type": "坐标 X", "value": 100},
                {"trait_type": "坐标 Y", "value": 200},
                {"trait_type": "面积", "value": "1000 m²"},
                {"trait_type": "区域", "value": "中心城"},
                {"trait_type": "稀有度", "value": "传说"}
            ]
        },
        {
            "type": "building",
            "name": "商业大厦 #042",
            "description": "现代化商业大厦，共 50 层，位于金融区核心位置。",
            "attributes": [
                {"trait_type": "楼层", "value": 50},
                {"trait_type": "容量", "value": "10000 人"},
                {"trait_type": "区域", "value": "金融区"},
                {"trait_type": "稀有度", "value": "史诗"}
            ]
        },
        {
            "type": "artwork",
            "name": "数字艺术 #123",
            "description": "由知名数字艺术家创作的抽象艺术作品。",
            "attributes": [
                {"trait_type": "艺术家", "value": "AI_Artist"},
                {"trait_type": "尺寸", "value": "4096x4096"},
                {"trait_type": "格式", "value": "PNG"},
                {"trait_type": "稀有度", "value": "稀有"}
            ]
        }
    ]
    
    for i, nft in enumerate(nft_examples, 1):
        print(f"\n   NFT #{i}:")
        print(f"   Type: {nft['type']}")
        print(f"   Name: {nft['name']}")
        print(f"   Desc: {nft['description'][:50]}...")
        print(f"   Attrs: {len(nft['attributes'])}")
    
    # 2. 创建元数据
    print("\n[Step 2] Create NFT Metadata...")
    
    for i, nft in enumerate(nft_examples, 1):
        metadata = create_nft_metadata(
            nft_type=nft['type'],
            name=nft['name'],
            description=nft['description'],
            attributes=nft['attributes']
        )
        
        # 模拟 IPFS URI
        ipfs_hash = f"Qm{''.join(['X'] * 44)}{i}"  # 模拟 IPFS 哈希
        token_uri = f"ipfs://{ipfs_hash}"
        
        print(f"\n   NFT #{i}:")
        print(f"   Token URI: {token_uri}")
        print(f"   元数据：{json.dumps(metadata, indent=2, ensure_ascii=False)[:200]}...")
    
    # 3. 模拟铸造
    print("\n[Step 3] Mint NFT...")
    
    contract_address = "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0"
    print(f"   合约地址：{contract_address}")
    print(f"   网络：localhost (Hardhat)")
    
    for i, nft in enumerate(nft_examples, 1):
        print(f"\n   Minting NFT #{i}...")
        print(f"   [OK] Transaction sent")
        print(f"   [WAIT] Waiting confirmation...")
        print(f"   [OK] Mint success!")
        print(f"   Token ID: {i}")
        print(f"   Owner: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")
    
    # 4. 查看结果
    print("\n[Step 4] View Results...")
    
    print("\n   Minted NFTs:")
    print("   " + "-"*50)
    for i, nft in enumerate(nft_examples, 1):
        print(f"   #{i}: {nft['name']}")
        print(f"       Type: {nft['type']}")
        print(f"       Rarity: {nft['attributes'][-1]['value']}")
        print()
    
    # 5. 总结
    print("\n" + "="*60)
    print("  [SUCCESS] NFT Mint Demo Complete!")
    print("="*60)
    print(f"\n   Total Minted: {len(nft_examples)} NFTs")
    print(f"   Total Gas: ~0.0015 ETH")
    print(f"   Avg per NFT: ~0.0005 ETH")
    print("\n   Next Steps:")
    print("   1. Visit http://localhost:3001/mint.html")
    print("   2. Click 'Mint NFT'")
    print("   3. Fill info and mint")
    print()

if __name__ == "__main__":
    try:
        demo_mint_flow()
    except KeyboardInterrupt:
        print("\n\n[WARN] Demo interrupted")
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
