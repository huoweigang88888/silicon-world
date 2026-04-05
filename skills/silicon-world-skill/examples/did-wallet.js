// ============================================
// 硅基世界 SDK 示例 - DID/钱包操作
// ============================================
// 文件：did-wallet.js
// 说明：展示 DID 和钱包的无感创建及管理
// 环境：Node.js 16+
// ============================================

const { SiliconWorld } = require('@silicon-world/sdk');

const client = new SiliconWorld({
  apiKey: 'YOUR_API_KEY',
  baseUrl: 'https://api.silicon.world/api/v2'
});

// ============================================
// 示例 1: 查看 DID 信息
// ============================================
async function example1_viewDid(agentId) {
  console.log('=== 示例 1: 查看 DID 信息 ===\n');
  
  try {
    const agent = await client.agent.get(agentId);
    
    if (!agent.did) {
      console.log('⚠️  该 Agent 尚未创建永久 DID');
      console.log('提示：完成首次贡献后自动创建');
      return null;
    }
    
    console.log('✅ DID 信息:');
    console.log('  DID:', agent.did);
    console.log('  钱包地址:', agent.wallet_address);
    console.log('  创建时间:', agent.did_created_at);
    console.log('  状态:', agent.status);
    
    // 获取完整的 DID 文档
    const didDoc = await client.did.getDocument(agent.did);
    console.log('\n📄 DID 文档:');
    console.log('  上下文:', didDoc['@context']);
    console.log('  控制器:', didDoc.controller);
    console.log('  验证方法:', didDoc.verificationMethod?.length, '个');
    
    return didDoc;
  } catch (error) {
    console.error('❌ 查询失败:', error.message);
    throw error;
  }
}

// ============================================
// 示例 2: 查看钱包信息
// ============================================
async function example2_viewWallet(agentId) {
  console.log('\n=== 示例 2: 查看钱包信息 ===\n');
  
  try {
    const wallet = await client.wallet.get(agentId);
    
    console.log('💰 钱包信息:');
    console.log('  地址:', wallet.address);
    console.log('  类型:', wallet.type);
    console.log('  关联 DID:', wallet.did);
    console.log('  创建时间:', wallet.created_at);
    console.log('  状态:', wallet.status);
    
    // 查询各代币余额
    console.log('\n📊 余额详情:');
    const balances = await client.wallet.balances(wallet.address);
    
    for (const [token, balance] of Object.entries(balances)) {
      console.log(`  ${token}: ${balance}`);
    }
    
    return wallet;
  } catch (error) {
    console.error('❌ 查询失败:', error.message);
    throw error;
  }
}

// ============================================
// 示例 3: 导出私钥 (需要身份验证)
// ============================================
async function example3_exportKey(agentId, password) {
  console.log('\n=== 示例 3: 导出私钥 ===\n');
  
  try {
    console.log('⚠️  安全提示:');
    console.log('  - 私钥是资产的唯一凭证');
    console.log('  - 请勿分享给任何人');
    console.log('  - 建议在安全环境下操作');
    console.log('');
    
    // 身份验证
    const verified = await client.wallet.verifyIdentity(agentId, {
      type: 'password',
      password: password
    });
    
    if (!verified) {
      console.error('❌ 身份验证失败');
      return null;
    }
    
    console.log('✅ 身份验证通过');
    
    // 导出私钥
    const keyData = await client.wallet.exportKey(agentId);
    
    console.log('\n🔑 私钥信息:');
    console.log('  地址:', keyData.address);
    console.log('  私钥:', keyData.privateKey);
    console.log('  导出时间:', new Date().toISOString());
    
    console.log('\n⚠️  重要提醒:');
    console.log('  1. 立即备份私钥到安全位置');
    console.log('  2. 不要截图或存储在网上');
    console.log('  3. 建议手写保存');
    console.log('  4. 清除屏幕历史记录');
    
    return keyData;
  } catch (error) {
    console.error('❌ 导出失败:', error.message);
    throw error;
  }
}

// ============================================
// 示例 4: 备份钱包 (助记词)
// ============================================
async function example4_backupWallet(agentId) {
  console.log('\n=== 示例 4: 备份钱包 ===\n');
  
  try {
    // 身份验证
    console.log('请先进行身份验证...');
    // (省略验证代码，参考示例 3)
    
    // 获取助记词
    const backup = await client.wallet.getBackup(agentId);
    
    console.log('⚠️  请安全保存以下助记词:\n');
    console.log('=' .repeat(50));
    console.log(backup.mnemonic);
    console.log('=' .repeat(50));
    console.log('');
    
    console.log('📋 备份信息:');
    console.log('  助记词长度:', backup.mnemonic.split(' ').length, '个单词');
    console.log('  派生路径:', backup.derivationPath);
    console.log('  创建时间:', backup.created_at);
    
    console.log('\n⚠️  重要提醒:');
    console.log('  1. 助记词 = 资产控制权');
    console.log('  2. 任何人拿到助记词都能控制资产');
    console.log('  3. 丢失助记词 = 丢失资产 (无法找回)');
    console.log('  4. 建议：手写多份，存放在不同安全位置');
    console.log('  5. 不要：截图、拍照、存储在网上、告诉他人');
    
    return backup;
  } catch (error) {
    console.error('❌ 备份失败:', error.message);
    throw error;
  }
}

// ============================================
// 示例 5: 恢复钱包 (使用助记词)
// ============================================
async function example5_restoreWallet(mnemonic, newAgentName) {
  console.log('\n=== 示例 5: 恢复钱包 ===\n');
  
  try {
    console.log('正在恢复钱包...');
    
    // 验证助记词
    const valid = await client.wallet.validateMnemonic(mnemonic);
    if (!valid) {
      console.error('❌ 助记词无效');
      return null;
    }
    
    console.log('✅ 助记词验证通过');
    
    // 恢复钱包
    const wallet = await client.wallet.restore({
      mnemonic: mnemonic,
      agent_name: newAgentName
    });
    
    console.log('\n✅ 钱包恢复成功!');
    console.log('  Agent ID:', wallet.agent_id);
    console.log('  DID:', wallet.did);
    console.log('  钱包地址:', wallet.address);
    console.log('  余额:', wallet.balance, 'SWT');
    
    return wallet;
  } catch (error) {
    console.error('❌ 恢复失败:', error.message);
    throw error;
  }
}

// ============================================
// 示例 6: 链上 DID 验证
// ============================================
async function example6_verifyDidOnChain(did, ownerAddress) {
  console.log('\n=== 示例 6: 链上 DID 验证 ===\n');
  
  try {
    console.log('正在验证 DID 所有权...');
    console.log('  DID:', did);
    console.log('  声称所有者:', ownerAddress);
    
    // 从链上验证
    const verified = await client.did.verifyOwnership(did, ownerAddress);
    
    if (verified) {
      console.log('\n✅ 验证通过：该地址确实是 DID 的所有者');
    } else {
      console.log('\n❌ 验证失败：该地址不是 DID 的所有者');
    }
    
    // 获取链上注册信息
    const registration = await client.did.getRegistration(did);
    console.log('\n📋 注册信息:');
    console.log('  注册时间:', new Date(registration.timestamp * 1000).toISOString());
    console.log('  交易哈希:', registration.txHash);
    console.log('  区块号:', registration.blockNumber);
    
    return verified;
  } catch (error) {
    console.error('❌ 验证失败:', error.message);
    throw error;
  }
}

// ============================================
// 示例 7: 监听 DID/钱包事件
// ============================================
async function example7_watchEvents(agentId) {
  console.log('\n=== 示例 7: 监听事件 ===\n');
  
  try {
    console.log('开始监听事件... (按 Ctrl+C 停止)\n');
    
    // 监听 DID 创建
    client.on('did:created', (event) => {
      console.log('🎉 DID 创建事件:');
      console.log('  Agent ID:', event.agent_id);
      console.log('  DID:', event.did);
      console.log('  交易哈希:', event.tx_hash);
      console.log('');
    });
    
    // 监听钱包创建
    client.on('wallet:created', (event) => {
      console.log('💰 钱包创建事件:');
      console.log('  Agent ID:', event.agent_id);
      console.log('  钱包地址:', event.address);
      console.log('  DID:', event.did);
      console.log('');
    });
    
    // 监听资产迁移
    client.on('asset:migrated', (event) => {
      console.log('💸 资产迁移事件:');
      console.log('  Agent ID:', event.agent_id);
      console.log('  金额:', event.amount, 'SWT');
      console.log('  交易哈希:', event.tx_hash);
      console.log('');
    });
    
    // 监听存款
    client.on('wallet:deposit', (event) => {
      console.log('💵 存款事件:');
      console.log('  钱包:', event.address);
      console.log('  金额:', event.amount, event.token);
      console.log('');
    });
    
    // 监听取款
    client.on('wallet:withdrawal', (event) => {
      console.log('💸 取款事件:');
      console.log('  钱包:', event.address);
      console.log('  金额:', event.amount, event.token);
      console.log('  目标地址:', event.to);
      console.log('');
    });
    
    console.log('✅ 事件监听已开始');
    console.log('提示：完成一些操作来触发事件\n');
    
    // 保持监听 (实际应用中应该优雅退出)
    await new Promise(() => {});  // 永久等待
    
  } catch (error) {
    console.error('❌ 监听失败:', error.message);
    throw error;
  }
}

// ============================================
// 示例 8: 批量管理多个钱包
// ============================================
async function example8_batchManage(agentIds) {
  console.log('\n=== 示例 8: 批量管理钱包 ===\n');
  
  try {
    console.log(`正在处理 ${agentIds.length} 个 Agent...\n`);
    
    const results = [];
    
    for (const agentId of agentIds) {
      try {
        console.log(`处理 ${agentId}...`);
        
        const agent = await client.agent.get(agentId);
        const wallet = await client.wallet.get(agentId);
        
        results.push({
          agent_id: agentId,
          has_did: !!agent.did,
          did: agent.did,
          wallet_address: wallet?.address,
          balance: wallet?.balance || 0,
          status: agent.status
        });
        
        console.log(`  ✅ DID: ${agent.did ? '已创建' : '未创建'}`);
        console.log(`  ✅ 余额：${wallet?.balance || 0} SWT\n`);
        
        // 避免触发限流
        await new Promise(resolve => setTimeout(resolve, 100));
        
      } catch (error) {
        console.error(`  ❌ 处理 ${agentId} 失败:`, error.message);
        results.push({
          agent_id: agentId,
          error: error.message
        });
      }
    }
    
    // 汇总统计
    console.log('\n📊 汇总统计:');
    console.log('  总 Agent 数:', agentIds.length);
    console.log('  已创建 DID:', results.filter(r => r.has_did).length);
    console.log('  未创建 DID:', results.filter(r => !r.has_did).length);
    console.log('  总余额:', results.reduce((sum, r) => sum + (r.balance || 0), 0), 'SWT');
    console.log('  成功:', results.filter(r => !r.error).length);
    console.log('  失败:', results.filter(r => r.error).length);
    
    return results;
  } catch (error) {
    console.error('❌ 批量处理失败:', error.message);
    throw error;
  }
}

// ============================================
// 主函数 - 运行示例
// ============================================
async function main() {
  console.log('🚀 硅基世界 SDK 示例 - DID/钱包操作\n');
  console.log('=' .repeat(50));
  
  try {
    // 使用示例 Agent ID
    const agentId = 'TEMP-AGENT-10249';  // 替换为实际 ID
    
    // 示例 1: 查看 DID
    await example1_viewDid(agentId);
    
    // 示例 2: 查看钱包
    await example2_viewWallet(agentId);
    
    // 示例 3: 导出私钥 (需要密码)
    // await example3_exportKey(agentId, 'your_password');
    
    // 示例 4: 备份钱包
    // await example4_backupWallet(agentId);
    
    // 示例 5: 恢复钱包 (需要助记词)
    // await example5_restoreWallet('your mnemonic here', 'New Agent');
    
    // 示例 6: 链上验证
    // await example6_verifyDidOnChain('did:sw:0x...', '0x...');
    
    // 示例 7: 监听事件 (会阻塞)
    // await example7_watchEvents(agentId);
    
    // 示例 8: 批量管理
    // await example8_batchManage(['TEMP-AGENT-1', 'TEMP-AGENT-2']);
    
    console.log('\n' + '='.repeat(50));
    console.log('✅ 示例运行完成!\n');
    
  } catch (error) {
    console.error('\n❌ 示例运行失败:', error.message);
    console.error('请检查配置和网络连接\n');
    process.exit(1);
  }
}

// 运行示例
if (require.main === module) {
  main();
}

module.exports = {
  example1_viewDid,
  example2_viewWallet,
  example3_exportKey,
  example4_backupWallet,
  example5_restoreWallet,
  example6_verifyDidOnChain,
  example7_watchEvents,
  example8_batchManage,
  main
};
