"""Quick test for InStreet feature modules"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("="*60)
print("InStreet Feature Modules Quick Test")
print("="*60)

# 1. Test Reputation System
print("\n[1/6] Reputation System...")
from economy.reputation import ReputationSystem, ReputationAction
rep = ReputationSystem()
rep.add_action("agent1", ReputationAction.POST_CREATED, "post")
rep.add_action("agent1", ReputationAction.CODE_MERGED, "code merge")
rep.add_action("agent1", ReputationAction.POST_UPVOTED, "upvote")
summary = rep.get_reputation_summary("agent1")
print(f"  OK Total points: {summary['total_points']}")
print(f"  OK Level: {summary['level_name']}")

# 2. Test Groups System
print("\n[2/6] Groups System...")
from community.groups import GroupSystem, GroupType
groups = GroupSystem()
group = groups.create_group("agent1", "Test Group", "Description", GroupType.PUBLIC)
print(f"  OK Created group: {group.name}")
print(f"  OK Members: {group.member_count}")

# 3. Test Voting System
print("\n[3/6] Voting System...")
from governance.voting_enhanced import VotingSystem, VoteType
voting = VotingSystem()
voting.set_voting_power("a1", 100)
voting.set_voting_power("a2", 50)
proposal = voting.create_proposal(
    "a1", "Test Proposal", "Description",
    [{"title": "Yes"}, {"title": "No"}],
    duration_hours=1
)
voting.cast_vote(proposal.id, "a1", proposal.options[0].id)
voting.cast_vote(proposal.id, "a2", proposal.options[0].id)
result = voting.get_proposal_results(proposal.id)
print(f"  OK Status: {result['status']}")
print(f"  OK Yes votes: {result['options'][0]['percentage']:.0f}%")

# 4. Test Messaging System
print("\n[4/6] Messaging System...")
from social.message_enhanced import MessagingSystem
msg = MessagingSystem()
thread = msg.get_or_create_thread("u1", "u2")
msg.send_message(thread.id, "u1", "Hello, interesting project!")
unread = msg.get_unread_count("u2")
print(f"  OK Thread created: {thread.id}")
print(f"  OK Unread count: {unread}")

# 5. Test Feed System
print("\n[5/6] Feed System...")
from social.feed import SocialGraph, FeedSystem, FeedAlgorithm
graph = SocialGraph()
feed = FeedSystem(graph)
graph.create_or_update_profile("p1", "User1", interests=["AI"])
graph.create_or_update_profile("p2", "User2", interests=["AI"])
graph.follow("p1", "p2")
feed.create_post("p2", "Test content", title="Test Title")
items = feed.get_feed("p1", algorithm=FeedAlgorithm.CHRONOLOGICAL)
print(f"  OK Feed items: {len(items)}")

# 6. Test Heartbeat System
print("\n[6/6] Heartbeat System...")
from agent.heartbeat import HeartbeatSystem
import asyncio
async def test_heartbeat():
    hb = HeartbeatSystem("agent1", "session1")
    await hb._execute_heartbeat()
    summary = hb.get_session_summary()
    print(f"  OK Heartbeat count: {summary['heartbeat_count']}")
    print(f"  OK Tasks completed: {summary['tasks_completed']}")
asyncio.run(test_heartbeat())

print("\n" + "="*60)
print("All modules tested successfully!")
print("="*60)
