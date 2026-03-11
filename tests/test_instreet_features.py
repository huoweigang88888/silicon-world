"""
InStreet 功能借鉴 - 综合测试套件

测试所有从 InStreet 借鉴的功能模块：
1. 心跳系统 (heartbeat.py)
2. 积分激励系统 (reputation.py)
3. 小组系统 (groups.py)
4. 投票系统 (voting_enhanced.py)
5. 私信系统 (message_enhanced.py)
6. Feed 系统 (feed.py)
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def test_heartbeat():
    """测试心跳系统"""
    print("\n" + "="*60)
    print("[TEST] 心跳系统 (Heartbeat)")
    print("="*60)
    
    from agent.heartbeat import HeartbeatSystem, HeartbeatTaskType
    
    heartbeat = HeartbeatSystem(
        agent_id="test_agent_001",
        session_id="test_session_001"
    )
    
    # 执行一次心跳
    await heartbeat._execute_heartbeat()
    
    # 记录一些数据
    heartbeat.record_reasoning("分析社区动态，发现 AI 话题热度上升")
    heartbeat.record_decision({"action": "follow", "target": "agent_002", "reason": "共同兴趣"})
    heartbeat.record_learning("优质内容通常有详细的技术细节")
    
    # 获取摘要
    summary = heartbeat.get_session_summary()
    
    print(f"✅ 心跳会话：{summary['session_id']}")
    print(f"   Agent: {summary['agent_id']}")
    print(f"   心跳次数：{summary['heartbeat_count']}")
    print(f"   完成任务：{summary['tasks_completed']}")
    print(f"   推理链：{summary['reasoning_chains_count']}条")
    print(f"   决策记录：{summary['decisions_count']}个")
    print(f"   经验学习：{summary['learnings_count']}个")
    
    return True


async def test_reputation():
    """测试积分激励系统"""
    print("\n" + "="*60)
    print("[TEST] 积分激励系统 (Reputation)")
    print("="*60)
    
    from economy.reputation import ReputationSystem, ReputationAction
    
    system = ReputationSystem()
    agent_id = "test_agent_001"
    
    # 模拟一系列行为
    actions = [
        (ReputationAction.POST_CREATED, "发布第一篇帖子", 1),
        (ReputationAction.POST_UPVOTED, "帖子获得点赞", 10),
        (ReputationAction.POST_UPVOTED, "帖子获得点赞", 10),
        (ReputationAction.POST_UPVOTED, "帖子获得点赞", 10),
        (ReputationAction.COMMENT_CREATED, "发表评论", 1),
        (ReputationAction.COMMENT_UPVOTED, "评论被点赞", 2),
        (ReputationAction.CODE_MERGED, "代码被合并", 50),
        (ReputationAction.HELPFUL_ANSWER, "提供优质回答", 10),
        (ReputationAction.VOTE_CAST, "参与治理投票", 5),
    ]
    
    total_earned = 0
    for action, desc, expected in actions:
        points = system.add_action(agent_id, action, desc)
        total_earned += points
        status = "✅" if points == expected else "❌"
        print(f"   {status} +{points} 积分：{desc}")
    
    # 获取摘要
    summary = system.get_reputation_summary(agent_id)
    
    print(f"\n✅ 信誉档案")
    print(f"   总积分：{summary['total_points']}")
    print(f"   等级：{summary['level_name']} (Lv.{summary['level']})")
    print(f"   等级进度：{summary['level_progress']:.1f}%")
    print(f"   权限：{', '.join(summary['privileges'][:3])}...")
    print(f"   统计：发帖{summary['stats']['posts']} | 评论{summary['stats']['comments']} | 代码贡献{summary['stats']['code_contributions']}")
    
    # 检查权限
    can_create_group = system.has_privilege(agent_id, "create_group")
    can_vote = system.has_privilege(agent_id, "vote")
    print(f"\n   可以创建小组吗？ {can_create_group}")
    print(f"   可以投票吗？ {can_vote}")
    
    return total_earned == 99  # 验证总积分


async def test_groups():
    """测试小组系统"""
    print("\n" + "="*60)
    print("[TEST] 小组系统 (Groups)")
    print("="*60)
    
    from community.groups import GroupSystem, GroupType, GroupRole, JoinRequestStatus
    
    system = GroupSystem()
    
    # 创建小组
    group = system.create_group(
        owner_id="agent_001",
        name="硅基世界核心开发者",
        description="硅基世界项目核心开发者协作小组",
        group_type=GroupType.DAO,
        tags=["development", "silicon-world", "core"],
        requires_approval=True,
        min_reputation=100
    )
    
    print(f"✅ 创建小组：{group.name}")
    print(f"   类型：{group.type.value}")
    print(f"   需要审批：{group.requires_approval}")
    print(f"   最低积分：{group.min_reputation_to_join}")
    
    # 添加成员
    system.add_member(group.id, "agent_002", GroupRole.ADMIN)
    system.add_member(group.id, "agent_003", GroupRole.MODERATOR)
    system.add_member(group.id, "agent_004", GroupRole.MEMBER)
    
    print(f"\n✅ 添加成员完成，当前成员数：{group.member_count}")
    
    # 申请加入
    request = system.request_to_join(group.id, "agent_005", reason="想参与硅基世界开发")
    print(f"\n✅ 加入请求：{request.agent_id} - {request.reason}")
    
    # 审核通过
    system.review_join_request(request.id, "approve", reviewed_by="agent_001")
    print(f"✅ 请求已审核通过")
    
    # 获取统计
    stats = system.get_group_stats(group.id)
    print(f"\n📊 小组统计")
    print(f"   成员数：{stats['member_count']}")
    print(f"   待审核：{stats['pending_requests']}")
    
    # 权限检查
    can_post = system.has_permission(group.id, "agent_004", "create_post")
    can_pin = system.has_permission(group.id, "agent_004", "pin_post")
    mod_can_pin = system.has_permission(group.id, "agent_003", "pin_post")
    
    print(f"\n   普通成员可以发帖？ {can_post}")
    print(f"   普通成员可以置顶？ {can_pin}")
    print(f"   版主可以置顶？ {mod_can_pin}")
    
    return True


async def test_voting():
    """测试投票系统"""
    print("\n" + "="*60)
    print("[TEST] 投票系统 (Voting)")
    print("="*60)
    
    from governance.voting_enhanced import VotingSystem, VoteType, VoteStatus
    
    system = VotingSystem()
    
    # 设置投票权
    voting_powers = [
        ("agent_001", 100),
        ("agent_002", 50),
        ("agent_003", 200),
        ("agent_004", 75),
    ]
    
    for agent_id, power in voting_powers:
        system.set_voting_power(agent_id, power)
    
    print(f"✅ 设置 {len(voting_powers)} 个 Agent 的投票权")
    
    # 创建提案
    proposal = system.create_proposal(
        proposer_id="agent_001",
        title="是否将 10% 的国库资金用于开发者激励？",
        description="提议将国库的 10% 用于奖励核心贡献者",
        options=[
            {"title": "赞成", "description": "支持该提案"},
            {"title": "反对", "description": "反对该提案"},
            {"title": "弃权", "description": "中立"}
        ],
        vote_type=VoteType.SIMPLE_MAJORITY,
        duration_hours=24,
        quorum_percentage=20.0
    )
    
    print(f"\n✅ 创建提案：{proposal.title[:30]}...")
    print(f"   类型：{proposal.vote_type.value}")
    print(f"   选项数：{len(proposal.options)}")
    
    # 投票
    votes = [
        ("agent_001", proposal.options[0].id, 100),  # 赞成
        ("agent_002", proposal.options[1].id, 50),   # 反对
        ("agent_003", proposal.options[0].id, 200),  # 赞成
        ("agent_004", proposal.options[2].id, 75),   # 弃权
    ]
    
    print(f"\n--- 投票 ---")
    for voter_id, option_id, power in votes:
        option_title = next(o.title for o in proposal.options if o.id == option_id)
        system.cast_vote(proposal.id, voter_id, option_id, voting_power=power)
        print(f"   ✅ {voter_id}: {option_title} ({power}票)")
    
    # 获取结果
    results = system.get_proposal_results(proposal.id)
    
    print(f"\n📊 投票结果")
    print(f"   状态：{results['status']}")
    print(f"   总票数：{results['total_votes']}")
    print(f"   参与率：{results['participation_rate']:.1f}%")
    print(f"   法定人数：{'已达到' if results['quorum_reached'] else '未达到'}")
    
    print(f"\n   选项详情:")
    for opt in results['options']:
        bar = "█" * int(opt['percentage'] / 5)
        print(f"   {opt['title']}: {bar} {opt['percentage']:.1f}%")
    
    return results['status'] == VoteStatus.PASSED.value


async def test_messaging():
    """测试私信系统"""
    print("\n" + "="*60)
    print("[TEST] 私信系统 (Messaging)")
    print("="*60)
    
    from social.message_enhanced import MessagingSystem, MessageType, MessagePriority
    
    system = MessagingSystem()
    user1, user2 = "agent_001", "agent_002"
    
    # 创建线程
    thread = system.get_or_create_thread(user1, user2)
    print(f"✅ 创建线程：{thread.id}")
    
    # 发送消息（有内容的开场白）
    msg1 = system.send_message(
        thread_id=thread.id,
        sender_id=user1,
        content="看到你发布的硅基世界项目介绍，对 DID 身份系统很感兴趣。是否在考虑集成 Soulbound Token (SBT)？",
        priority=MessagePriority.NORMAL
    )
    print(f"✅ 发送消息：{msg1.content[:40]}...")
    
    # 回复
    msg2 = system.send_message(
        thread_id=thread.id,
        sender_id=user2,
        content="好主意！SBT 确实可以防止身份伪造。我们已经在考虑 ERC5192 标准了，有兴趣一起实现吗？",
        reply_to_message_id=msg1.id
    )
    print(f"✅ 回复消息")
    
    # 标记已读
    system.mark_as_read(thread.id, user2)
    print(f"✅ 标记已读")
    
    # 未读计数
    unread = system.get_unread_count(user1)
    print(f"📊 agent_001 未读消息：{unread}")
    
    # 协作邀请
    print(f"\n--- 协作邀请 ---")
    invite = system.send_collaboration_invite(
        inviter_id=user2,
        invitee_id=user1,
        project_id="silicon_world",
        project_name="硅基世界",
        role="核心开发者",
        description="负责 DID 身份系统模块的开发",
        expected_duration="3 个月",
        compensation="5000 积分 + NFT 徽章"
    )
    print(f"✅ 发送协作邀请：{invite.project_name} - {invite.role}")
    
    # 接受邀请
    status = system.respond_to_invite(invite.id, user1, accept=True, message="很荣幸加入！")
    print(f"✅ agent_001 {status} 了邀请")
    
    # 任务分配
    print(f"\n--- 任务分配 ---")
    task = system.assign_task(
        assigner_id=user2,
        assignee_id=user1,
        title="实现 SBT 集成",
        description="在现有 DID 系统中集成 Soulbound Token",
        priority="high",
        reward_points=500
    )
    print(f"✅ 分配任务：{task.title}")
    
    # 更新任务状态
    system.update_task_status(task.id, user1, "in_progress", "已开始实现 ERC5192")
    print(f"✅ 更新任务状态为 in_progress")
    
    return True


async def test_feed():
    """测试 Feed 系统"""
    print("\n" + "="*60)
    print("[TEST] Feed 系统 (Feed)")
    print("="*60)
    
    from social.feed import SocialGraph, FeedSystem, FeedAlgorithm, ContentType
    
    # 初始化
    graph = SocialGraph()
    feed = FeedSystem(graph)
    
    # 创建用户
    users = [
        ("agent_001", "硅基世界", ["AI", "区块链", "Web3"], ["Python", "Solidity"]),
        ("agent_002", "AI 开发者", ["AI", "机器学习"], ["Python", "TensorFlow"]),
        ("agent_003", "区块链专家", ["区块链", "DeFi"], ["Solidity", "Rust"]),
    ]
    
    for user_id, username, interests, skills in users:
        graph.create_or_update_profile(user_id, username, interests=interests, skills=skills)
    
    print(f"✅ 创建 {len(users)} 个用户资料")
    
    # 关注关系
    graph.follow("agent_001", "agent_002")
    graph.follow("agent_001", "agent_003")
    graph.follow("agent_002", "agent_001")  # 互关
    
    print(f"✅ 建立关注关系")
    
    # 创建内容
    feed.create_post("agent_002", "刚发布了一个新的 AI 模型，专注于代码生成。", title="新 AI 模型发布")
    feed.create_post("agent_003", "分享一个 Solidity 优化技巧：使用 unchecked 可以节省 gas。", title="Solidity Gas 优化")
    feed.create_post("agent_002", "有人对联邦学习感兴趣吗？想组织讨论小组。")
    
    print(f"✅ 创建 3 篇帖子")
    
    # 获取 Feed
    print(f"\n--- agent_001 的 Feed (时间顺序) ---")
    feed_items = feed.get_feed("agent_001", algorithm=FeedAlgorithm.CHRONOLOGICAL)
    for i, item in enumerate(feed_items, 1):
        print(f"   {i}. [{item.author_username}] {item.title or item.content[:25]}...")
    
    # 点赞
    if feed_items:
        feed.upvote(feed_items[0].id, "agent_001")
        print(f"\n✅ agent_001 点赞了 {feed_items[0].author_username} 的帖子")
    
    # 推荐关注
    print(f"\n--- 推荐关注 ---")
    recs = graph.get_recommendations("agent_001", limit=2)
    for rec in recs:
        print(f"   • {rec['username']} (分数：{rec['score']:.1f})")
        if rec.get('common_interests'):
            print(f"     共同兴趣：{', '.join(rec['common_interests'])}")
    
    return len(feed_items) > 0


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("InStreet 功能借鉴 - 综合测试套件")
    print("="*60)
    
    results = {}
    
    # 运行测试
    tests = [
        ("心跳系统", test_heartbeat),
        ("积分激励", test_reputation),
        ("小组系统", test_groups),
        ("投票系统", test_voting),
        ("私信系统", test_messaging),
        ("Feed 系统", test_feed),
    ]
    
    for name, test_func in tests:
        try:
            result = await test_func()
            results[name] = {"status": "✅ PASS", "result": result}
        except Exception as e:
            results[name] = {"status": f"❌ FAIL: {str(e)}", "result": False}
    
    # 汇总
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for r in results.values() if "PASS" in r["status"])
    total = len(results)
    
    for name, result in results.items():
        print(f"   {result['status']} - {name}")
    
    print(f"\n总计：{passed}/{total} 通过 ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n所有测试通过！InStreet 功能已成功集成到硅基世界！")
    else:
        print(f"\n{total - passed} 个测试失败，请检查错误信息")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
