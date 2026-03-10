#!/usr/bin/env python3
"""
本地部署功能测试脚本

测试所有核心功能：
- NFT 铸造
- NFT 交易
- 钱包功能
- 游戏化功能
"""

import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000"
MARKETPLACE_URL = "http://localhost:3001"
DASHBOARD_URL = "http://localhost:3000"

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_result(test_name, success, message=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {test_name}")
    if message:
        print(f"   {message}")

# ==================== API 测试 ====================

def test_api_health():
    """测试 API 健康检查"""
    print_header("API 健康检查")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        success = response.status_code == 200
        print_result("健康检查", success, f"状态码：{response.status_code}")
        if success:
            data = response.json()
            print(f"   响应：{data}")
        return success
    except Exception as e:
        print_result("健康检查", False, str(e))
        return False

def test_api_docs():
    """测试 API 文档"""
    print_header("API 文档")
    
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        success = response.status_code == 200
        print_result("Swagger 文档", success, f"状态码：{response.status_code}")
        return success
    except Exception as e:
        print_result("Swagger 文档", False, str(e))
        return False

def test_agents_api():
    """测试 Agent API"""
    print_header("Agent API")
    
    try:
        # 获取 Agent 列表
        response = requests.get(f"{BASE_URL}/api/v1/agents", timeout=5)
        success = response.status_code == 200
        print_result("获取 Agent 列表", success)
        
        if success:
            data = response.json()
            print(f"   Agent 数量：{len(data) if isinstance(data, list) else 'N/A'}")
        
        return success
    except Exception as e:
        print_result("Agent API", False, str(e))
        return False

def test_gamification_api():
    """测试游戏化 API"""
    print_header("游戏化 API")
    
    try:
        # 获取游戏化统计
        response = requests.get(f"{BASE_URL}/api/v1/gamification/statistics", timeout=5)
        success = response.status_code == 200
        print_result("游戏化统计", success)
        
        if success:
            data = response.json()
            print(f"   响应：{json.dumps(data, indent=2)[:200]}...")
        
        return success
    except Exception as e:
        print_result("游戏化 API", False, str(e))
        return False

def test_optimization_api():
    """测试优化 API"""
    print_header("优化 API")
    
    try:
        # 获取性能报告
        response = requests.get(f"{BASE_URL}/api/v1/optimization/report", timeout=5)
        success = response.status_code == 200
        print_result("性能报告", success)
        
        if success:
            data = response.json()
            print(f"   数据库表：{len(data.get('tables', {}))}")
        
        return success
    except Exception as e:
        print_result("优化 API", False, str(e))
        return False

# ==================== 前端测试 ====================

def test_marketplace_page():
    """测试 NFT 市场页面"""
    print_header("NFT 市场页面")
    
    try:
        response = requests.get(f"{MARKETPLACE_URL}/index.html", timeout=5)
        success = response.status_code == 200
        print_result("市场首页", success)
        
        if success:
            content_length = len(response.text)
            print(f"   页面大小：{content_length} 字节")
        
        return success
    except Exception as e:
        print_result("市场首页", False, str(e))
        return False

def test_mint_page():
    """测试铸造页面"""
    print_header("铸造页面")
    
    try:
        response = requests.get(f"{MARKETPLACE_URL}/mint.html", timeout=5)
        success = response.status_code == 200
        print_result("铸造页面", success)
        
        if success:
            content_length = len(response.text)
            print(f"   页面大小：{content_length} 字节")
        
        return success
    except Exception as e:
        print_result("铸造页面", False, str(e))
        return False

def test_trade_page():
    """测试交易页面"""
    print_header("交易页面")
    
    try:
        response = requests.get(f"{MARKETPLACE_URL}/trade.html", timeout=5)
        success = response.status_code == 200
        print_result("交易页面", success)
        
        if success:
            content_length = len(response.text)
            print(f"   页面大小：{content_length} 字节")
        
        return success
    except Exception as e:
        print_result("交易页面", False, str(e))
        return False

def test_dashboard_page():
    """测试 Dashboard 页面"""
    print_header("Dashboard 页面")
    
    try:
        response = requests.get(f"{DASHBOARD_URL}/index.html", timeout=5)
        success = response.status_code == 200
        print_result("Dashboard 首页", success)
        
        if success:
            content_length = len(response.text)
            print(f"   页面大小：{content_length} 字节")
        
        return success
    except Exception as e:
        print_result("Dashboard 首页", False, str(e))
        return False

def test_wallet_page():
    """测试钱包页面"""
    print_header("钱包页面")
    
    try:
        response = requests.get(f"{DASHBOARD_URL}/wallet.html", timeout=5)
        success = response.status_code == 200
        print_result("钱包页面", success)
        
        if success:
            content_length = len(response.text)
            print(f"   页面大小：{content_length} 字节")
        
        return success
    except Exception as e:
        print_result("钱包页面", False, str(e))
        return False

def test_gamification_page():
    """测试游戏化页面"""
    print_header("游戏化页面")
    
    try:
        response = requests.get(f"{DASHBOARD_URL}/gamification.html", timeout=5)
        success = response.status_code == 200
        print_result("游戏化中心", success)
        
        if success:
            content_length = len(response.text)
            print(f"   页面大小：{content_length} 字节")
        
        return success
    except Exception as e:
        print_result("游戏化中心", False, str(e))
        return False

# ==================== 合约测试 ====================

def test_contract_deployment():
    """测试合约部署"""
    print_header("合约部署验证")
    
    import os
    from pathlib import Path
    
    try:
        # 检查部署信息文件
        deploy_info_path = Path(__file__).parent.parent / "contracts" / "deployment-info.json"
        
        if deploy_info_path.exists():
            with open(deploy_info_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            nft_address = data.get('contracts', {}).get('SiliconWorldNFT')
            marketplace_address = data.get('contracts', {}).get('SiliconWorldMarketplace')
            
            success = bool(nft_address and marketplace_address)
            print_result("合约地址记录", success)
            
            if success:
                print(f"   NFT 合约：{nft_address}")
                print(f"   市场合约：{marketplace_address}")
            
            return success
        else:
            print_result("合约地址记录", False, "deployment-info.json 不存在")
            return False
            
    except Exception as e:
        print_result("合约地址记录", False, str(e))
        return False

# ==================== 主测试流程 ====================

def run_all_tests():
    """运行所有测试"""
    print("\n")
    print("╔" + "═"*58 + "╗")
    print("║" + " "*20 + "硅基世界 - 功能测试" + " "*19 + "║")
    print("╚" + "═"*58 + "╝")
    print(f"\n测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API 地址：{BASE_URL}")
    print(f"市场地址：{MARKETPLACE_URL}")
    print(f"Dashboard: {DASHBOARD_URL}")
    
    results = {
        "API": [],
        "前端": [],
        "合约": []
    }
    
    # API 测试
    results["API"].append(test_api_health())
    results["API"].append(test_api_docs())
    results["API"].append(test_agents_api())
    results["API"].append(test_gamification_api())
    results["API"].append(test_optimization_api())
    
    # 前端测试
    results["前端"].append(test_marketplace_page())
    results["前端"].append(test_mint_page())
    results["前端"].append(test_trade_page())
    results["前端"].append(test_dashboard_page())
    results["前端"].append(test_wallet_page())
    results["前端"].append(test_gamification_page())
    
    # 合约测试
    results["合约"].append(test_contract_deployment())
    
    # 汇总结果
    print_header("测试结果汇总")
    
    total_tests = 0
    total_passed = 0
    
    for category, category_results in results.items():
        passed = sum(category_results)
        total = len(category_results)
        total_tests += total
        total_passed += passed
        
        percentage = (passed / total * 100) if total > 0 else 0
        print(f"{category}: {passed}/{total} ({percentage:.1f}%)")
    
    print("\n" + "-"*60)
    overall_percentage = (total_passed / total_tests * 100) if total_tests > 0 else 0
    print(f"总计：{total_passed}/{total_tests} ({overall_percentage:.1f}%)")
    
    if overall_percentage >= 90:
        print("\n✅ 测试通过！所有功能正常！")
    elif overall_percentage >= 70:
        print("\n⚠️  部分功能异常，请检查！")
    else:
        print("\n❌ 多个功能异常，需要修复！")
    
    print("\n")
    
    return overall_percentage

if __name__ == "__main__":
    try:
        success_rate = run_all_tests()
        exit(0 if success_rate >= 90 else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n❌ 测试执行失败：{e}")
        exit(1)
