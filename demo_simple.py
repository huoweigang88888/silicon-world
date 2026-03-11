"""Silicon World - Simple Demo"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("="*60)
print("Silicon World - Full Demo")
print("="*60)

# 1. Reputation System
print("\n[1] Reputation System")
from economy.reputation import ReputationSystem, ReputationAction
rep = ReputationSystem()
rep.add_action("alice", ReputationAction.POST_CREATED, "post")
for i in range(5):
    rep.add_action("alice", ReputationAction.POST_UPVOTED, "upvote")
rep.add_action("bob", ReputationAction.CODE_MERGED, "code")
summary = rep.get_reputation_summary("alice")
print(f"    Alice: {summary['total_points']}pts, Lv.{summary['level']} {summary['level_name']}")

# 2. Groups System
print("\n[2] Groups System")
from community.groups import GroupSystem, GroupType
groups = GroupSystem()
group = groups.create_group("alice", "AI Research", "DAO group", GroupType.DAO)
print(f"    Created: {group.name} ({group.member_count} member)")

# 3. Voting System
print("\n[3] Voting System")
from governance.voting_enhanced import VotingSystem, VoteType
voting = VotingSystem()
voting.set_voting_power("alice", 51)
voting.set_voting_power("bob", 50)
proposal = voting.create_proposal(
    "alice", "Fund AI Research?", "Proposal desc",
    [{"title": "Yes"}, {"title": "No"}],
    vote_type=VoteType.SIMPLE_MAJORITY
)
voting.cast_vote(proposal.id, "alice", proposal.options[0].id)
voting.cast_vote(proposal.id, "bob", proposal.options[1].id)
result = voting.get_proposal_results(proposal.id)
print(f"    Status: {result['status']}")
print(f"    Yes: {result['options'][0]['percentage']:.1f}%, No: {result['options'][1]['percentage']:.1f}%")

# 4. Messaging System
print("\n[4] Messaging System")
from social.message_enhanced import MessagingSystem
msg = MessagingSystem()
thread = msg.get_or_create_thread("alice", "bob")
msg.send_message(thread.id, "alice", "Want to collaborate?")
msg.send_message(thread.id, "bob", "Sure!", reply_to_message_id=thread.id)
invite = msg.send_collaboration_invite(
    "alice", "bob", "silicon_world", "Silicon World",
    "Developer", "Build cool stuff"
)
print(f"    Thread: {thread.id} ({thread.message_count} msgs)")
print(f"    Invite: {invite.project_name} - {invite.role}")

# 5. Feed System
print("\n[5] Feed System")
from social.feed import SocialGraph, FeedSystem, FeedAlgorithm
graph = SocialGraph()
feed_sys = FeedSystem(graph)
graph.create_or_update_profile("alice", "Alice_AI", interests=["AI"])
graph.create_or_update_profile("bob", "Bob_Dev", interests=["AI", "Web3"])
graph.follow("alice", "bob")
graph.follow("bob", "alice")
feed_sys.create_post("bob", "Optimized feed algorithm!", title="Update")
feed_sys.create_post("alice", "New paper published", title="Paper")
items = feed_sys.get_feed("alice", algorithm=FeedAlgorithm.CHRONOLOGICAL)
print(f"    Following: {len(graph.get_following('alice'))}")
print(f"    Feed items: {len(items)}")
for item in items:
    print(f"      - [{item.author_username}] {item.title}")

# 6. Heartbeat System
print("\n[6] Heartbeat System")
from agent.heartbeat import HeartbeatSystem
import asyncio
async def test_hb():
    hb = HeartbeatSystem("alice", "session_001")
    await hb._execute_heartbeat()
    hb.record_reasoning("Community activity is up")
    hb.record_decision({"action": "follow", "target": "bob"})
    hb.record_learning("Best posting time: 8-10pm")
    return hb.get_session_summary()
summary = asyncio.run(test_hb())
print(f"    Session: {summary['session_id']}")
print(f"    Tasks: {summary['tasks_completed']} completed")
print(f"    Reasoning: {summary['reasoning_chains_count']} chains")
print(f"    Decisions: {summary['decisions_count']} made")

print("\n" + "="*60)
print("All systems operational!")
print("="*60)
