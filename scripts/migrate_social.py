"""
社交系统 - 数据库迁移
添加社交功能相关的表
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "silicon_world.db"

def migrate():
    """执行数据库迁移"""
    
    print(f"[MIGRATE] Starting social system migration: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. 好友关系表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friendships (
            id TEXT PRIMARY KEY,
            agent_id_1 TEXT NOT NULL,
            agent_id_2 TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id_1) REFERENCES agents(id),
            FOREIGN KEY (agent_id_2) REFERENCES agents(id)
        )
    """)
    print("[OK] friendships table")
    
    # 2. 关注关系表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS follows (
            id TEXT PRIMARY KEY,
            follower_id TEXT NOT NULL,
            following_id TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (follower_id) REFERENCES agents(id),
            FOREIGN KEY (following_id) REFERENCES agents(id)
        )
    """)
    print("[OK] follows table")
    
    # 3. 消息表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            sender_id TEXT NOT NULL,
            receiver_id TEXT,
            group_id TEXT,
            content TEXT NOT NULL,
            message_type TEXT DEFAULT 'text',
            data JSON DEFAULT '{}',
            is_read INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES agents(id),
            FOREIGN KEY (receiver_id) REFERENCES agents(id),
            FOREIGN KEY (group_id) REFERENCES groups(id)
        )
    """)
    print("[OK] messages table")
    
    # 4. 群组表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            owner_id TEXT NOT NULL,
            max_members INTEGER DEFAULT 50,
            is_public INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES agents(id)
        )
    """)
    print("[OK] groups table")
    
    # 5. 群组成员表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS group_members (
            id TEXT PRIMARY KEY,
            group_id TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            role TEXT DEFAULT 'member',
            joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (group_id) REFERENCES groups(id),
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    """)
    print("[OK] group_members table")
    
    # 6. 通知表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            data JSON DEFAULT '{}',
            is_read INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    """)
    print("[OK] notifications table")
    
    # 7. 屏蔽表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocks (
            id TEXT PRIMARY KEY,
            blocker_id TEXT NOT NULL,
            blocked_id TEXT NOT NULL,
            reason TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (blocker_id) REFERENCES agents(id),
            FOREIGN KEY (blocked_id) REFERENCES agents(id)
        )
    """)
    print("[OK] blocks table")
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_friendships_agent1 ON friendships(agent_id_1)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_friendships_agent2 ON friendships(agent_id_2)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_follows_follower ON follows(follower_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_follows_following ON follows(following_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_agent ON notifications(agent_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_blocks_blocker ON blocks(blocker_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_blocks_blocked ON blocks(blocked_id)")
    print("[OK] Indexes created")
    
    conn.commit()
    conn.close()
    
    print("\n[MIGRATE] Social system migration completed!")

if __name__ == "__main__":
    migrate()
