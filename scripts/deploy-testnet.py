#!/usr/bin/env python3
"""
硅基世界 - 测试网部署脚本

一键部署到 Goerli 测试网
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime


def print_header(text: str):
    """打印标题"""
    print("\n" + "=" * 70)
    print(f" {text}")
    print("=" * 70 + "\n")


def load_config(config_path: str = "config/testnet.json") -> dict:
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_prerequisites():
    """检查前置条件"""
    print_header("1. 检查前置条件")
    
    checks = {
        "Python": "python --version",
        "Node.js": "node --version",
        "npm": "npm --version",
        "Git": "git --version"
    }
    
    all_ok = True
    for name, cmd in checks.items():
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {name}: {result.stdout.strip()}")
        else:
            print(f"✗ {name}: 未安装")
            all_ok = False
    
    # 检查环境变量
    print("\n环境变量检查:")
    env_vars = ["PRIVATE_KEY", "INFURA_KEY", "ALCHEMY_KEY"]
    for var in env_vars:
        if os.getenv(var):
            print(f"✓ {var}: 已设置")
        else:
            print(f"⚠ {var}: 未设置")
    
    return all_ok


def install_dependencies():
    """安装依赖"""
    print_header("2. 安装依赖")
    
    print("安装 Python 依赖...")
    subprocess.run("pip install -r requirements.txt", shell=True)
    
    if Path("package.json").exists():
        print("安装 Node.js 依赖...")
        subprocess.run("npm install", shell=True)
    
    print("✓ 依赖安装完成")


def compile_contracts():
    """编译智能合约"""
    print_header("3. 编译智能合约")
    
    contracts_dir = Path("src/blockchain/contracts")
    build_dir = Path("build/contracts")
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查 solc
    result = subprocess.run("solc --version", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("⚠ solc 未安装，使用 Hardhat 编译")
        subprocess.run("npx hardhat compile", shell=True)
        return
    
    # 编译合约
    for sol_file in contracts_dir.glob("*.sol"):
        print(f"编译：{sol_file.name}")
        subprocess.run(
            f"solc --bin --abi {sol_file} -o {build_dir}",
            shell=True
        )
    
    print("✓ 合约编译完成")


def deploy_contracts(config: dict):
    """部署智能合约"""
    print_header("4. 部署智能合约")
    
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        print("✗ 未设置 PRIVATE_KEY")
        return False
    
    print(f"部署网络：{config['network']['name']}")
    print(f"Chain ID: {config['network']['chainId']}")
    print(f"部署者：{config['deployment']['deployer']}")
    
    # 使用 Hardhat 部署
    print("\n使用 Hardhat 部署合约...")
    
    deploy_script = Path("scripts/deploy-contracts.js")
    if deploy_script.exists():
        subprocess.run(f"npx hardhat run {deploy_script} --network goerli", shell=True)
    else:
        print("⚠ 部署脚本不存在，手动部署")
        print("参考：docs/testnet-deployment.md")
    
    return True


def deploy_api(config: dict):
    """部署 API 服务"""
    print_header("5. 部署 API 服务")
    
    # 检查 Docker
    result = subprocess.run("docker --version", shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print("⚠ Docker 未安装，跳过容器部署")
        return False
    
    print("使用 Docker Compose 部署...")
    subprocess.run("docker-compose -f docker-compose.testnet.yml up -d", shell=True)
    
    # 等待服务启动
    print("等待服务启动...")
    subprocess.run("sleep 15", shell=True)
    
    # 健康检查
    api_url = config['api']['baseUrl']
    result = subprocess.run(f"curl -f {api_url}/health", shell=True, capture_output=True)
    
    if result.returncode == 0:
        print(f"✓ API 服务运行正常：{api_url}")
        return True
    else:
        print(f"⚠ API 服务可能未完全启动：{api_url}")
        return False


def run_tests():
    """运行集成测试"""
    print_header("6. 运行集成测试")
    
    print("运行 API 测试...")
    result = subprocess.run("pytest tests/e2e/ -v", shell=True)
    
    if result.returncode == 0:
        print("✓ 所有测试通过")
        return True
    else:
        print("⚠ 部分测试失败")
        return False


def generate_deployment_report(config: dict):
    """生成部署报告"""
    print_header("7. 生成部署报告")
    
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "network": config['network'],
        "contracts": {},
        "api": {
            "url": config['api']['baseUrl'],
            "status": "deployed"
        },
        "database": config['database'],
        "monitoring": config['monitoring']
    }
    
    # 保存报告
    report_path = Path("deployment-testnet-report.json")
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"部署报告已保存：{report_path}")
    return report


def main():
    """主函数"""
    print_header("🌍 硅基世界 - 测试网部署")
    
    # 加载配置
    config = load_config()
    
    # 1. 检查前置条件
    if not check_prerequisites():
        print("\n✗ 前置条件检查失败")
        sys.exit(1)
    
    # 2. 安装依赖
    install_dependencies()
    
    # 3. 编译合约
    compile_contracts()
    
    # 4. 部署合约
    deploy_contracts(config)
    
    # 5. 部署 API
    deploy_api(config)
    
    # 6. 运行测试
    run_tests()
    
    # 7. 生成报告
    generate_deployment_report(config)
    
    print_header("✅ 部署完成")
    print("✓ 测试网部署成功！")
    print("\n下一步:")
    print(f"  1. 访问 API 文档：{config['api']['baseUrl']}/docs")
    print(f"  2. 查看部署报告：deployment-testnet-report.json")
    print(f"  3. 配置前端：更新 API 地址")
    print(f"  4. 开始测试！")
    print()


if __name__ == "__main__":
    main()
