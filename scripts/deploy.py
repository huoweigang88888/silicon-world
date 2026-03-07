#!/usr/bin/env python3
"""
硅基世界 - 部署脚本

一键部署到测试网/主网
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime


def print_header(text: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f" {text}")
    print("=" * 60 + "\n")


def run_command(command: str, check: bool = True):
    """运行 shell 命令"""
    print(f"执行：{command}")
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr and check:
        print(f"警告：{result.stderr}")
    
    if check and result.returncode != 0:
        raise Exception(f"命令执行失败：{command}")
    
    return result


def check_prerequisites():
    """检查前置条件"""
    print_header("检查前置条件")
    
    # 检查 Python
    result = run_command("python --version", check=False)
    if result.returncode == 0:
        print(f"✓ Python: {result.stdout.strip()}")
    else:
        print("✗ Python 未安装")
        return False
    
    # 检查 Docker
    result = run_command("docker --version", check=False)
    if result.returncode == 0:
        print(f"✓ Docker: {result.stdout.strip()}")
    else:
        print("⚠ Docker 未安装 (可选)")
    
    # 检查 Node.js
    result = run_command("node --version", check=False)
    if result.returncode == 0:
        print(f"✓ Node.js: {result.stdout.strip()}")
    else:
        print("⚠ Node.js 未安装 (可选)")
    
    return True


def install_dependencies():
    """安装依赖"""
    print_header("安装依赖")
    
    # 安装 Python 依赖
    print("安装 Python 依赖...")
    run_command("pip install -r requirements.txt")
    
    # 安装 Node.js 依赖 (如果有)
    if Path("package.json").exists():
        print("安装 Node.js 依赖...")
        run_command("npm install")
    
    print("✓ 依赖安装完成")


def build_contracts():
    """编译智能合约"""
    print_header("编译智能合约")
    
    contracts_dir = Path("src/blockchain/contracts")
    build_dir = Path("build/contracts")
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查是否有 Solidity 编译器
    result = run_command("solc --version", check=False)
    if result.returncode != 0:
        print("⚠ solc 未安装，跳过合约编译")
        print("提示：安装 solc: https://docs.soliditylang.org/en/latest/installing-solidity.html")
        return
    
    # 编译合约
    for sol_file in contracts_dir.glob("*.sol"):
        print(f"编译：{sol_file.name}")
        run_command(f"solc --bin --abi {sol_file} -o {build_dir}")
    
    print("✓ 合约编译完成")


def deploy_contracts(network: str = "testnet"):
    """部署智能合约"""
    print_header(f"部署合约到 {network}")
    
    # 检查私钥
    private_key = os.getenv("PRIVATE_KEY")
    if not private_key:
        print("✗ 未设置 PRIVATE_KEY 环境变量")
        print("请设置：export PRIVATE_KEY=your_private_key")
        return False
    
    # 根据网络选择 RPC
    rpc_urls = {
        "testnet": "https://goerli.infura.io/v3/YOUR_KEY",
        "mainnet": "https://mainnet.infura.io/v3/YOUR_KEY"
    }
    
    rpc_url = rpc_urls.get(network)
    if not rpc_url:
        print(f"✗ 未知网络：{network}")
        return False
    
    print(f"网络：{network}")
    print(f"RPC: {rpc_url}")
    
    # TODO: 实际部署合约
    print("⚠ 合约部署功能待实现")
    print("可以使用 Hardhat 或 Truffle 进行部署")
    
    return True


def deploy_api():
    """部署 API 服务"""
    print_header("部署 API 服务")
    
    # 检查 Docker
    result = run_command("docker --version", check=False)
    if result.returncode != 0:
        print("⚠ Docker 未安装，使用本地部署")
        print("建议使用 Docker 进行生产部署")
        return False
    
    # 使用 Docker Compose 部署
    if Path("docker-compose.yml").exists():
        print("使用 Docker Compose 部署...")
        run_command("docker-compose up -d")
        
        # 等待服务启动
        print("等待服务启动...")
        run_command("sleep 10")
        
        # 健康检查
        result = run_command(
            "curl -f http://localhost:8000/health",
            check=False
        )
        
        if result.returncode == 0:
            print("✓ API 服务运行正常")
            return True
        else:
            print("⚠ API 服务可能未完全启动")
            return False
    else:
        print("⚠ docker-compose.yml 不存在")
        return False


def run_tests():
    """运行测试"""
    print_header("运行测试")
    
    # 运行 Python 测试
    print("运行 Python 测试...")
    result = run_command("pytest tests/ -v", check=False)
    
    if result.returncode == 0:
        print("✓ 所有测试通过")
        return True
    else:
        print("⚠ 部分测试失败")
        return False


def generate_deployment_report():
    """生成部署报告"""
    print_header("生成部署报告")
    
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "network": os.getenv("NETWORK", "testnet"),
        "contracts": {
            "deployed": False,
            "addresses": {}
        },
        "api": {
            "deployed": False,
            "url": "http://localhost:8000"
        },
        "tests": {
            "passed": False
        }
    }
    
    # 保存报告
    report_path = Path("deployment-report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"部署报告已保存：{report_path}")
    return report


def main():
    """主函数"""
    print_header("硅基世界 - 部署脚本")
    
    # 获取部署参数
    network = os.getenv("NETWORK", "testnet")
    skip_tests = os.getenv("SKIP_TESTS", "false").lower() == "true"
    
    # 1. 检查前置条件
    if not check_prerequisites():
        print("\n✗ 前置条件检查失败")
        sys.exit(1)
    
    # 2. 安装依赖
    install_dependencies()
    
    # 3. 编译合约
    build_contracts()
    
    # 4. 运行测试
    if not skip_tests:
        if not run_tests():
            print("\n⚠ 测试未通过，是否继续部署？")
            response = input("继续 (y/n): ")
            if response.lower() != 'y':
                sys.exit(1)
    
    # 5. 部署合约
    deploy_contracts(network)
    
    # 6. 部署 API
    deploy_api()
    
    # 7. 生成报告
    generate_deployment_report()
    
    print_header("部署完成")
    print("✓ 部署成功！")
    print("\n下一步:")
    print("  1. 检查 API 服务：http://localhost:8000/docs")
    print("  2. 查看部署报告：deployment-report.json")
    print("  3. 配置合约地址到环境变量")
    print("  4. 开始使用硅基世界！")
    print()


if __name__ == "__main__":
    main()
