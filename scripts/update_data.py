"""
更新旧 Agent 数据
为旧记录设置默认值
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "silicon_world.db"

def update_old_data():
    """更新旧数据"""
    
    print(f"[UPDATE] Updating old data in: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 更新 agents 表
    cursor.execute("""
        UPDATE agents 
        SET 
            agent_type = COALESCE(agent_type, 'native'),
            connection = COALESCE(connection, '{}'),
            capabilities = COALESCE(capabilities, '[]'),
            status = COALESCE(status, 'unknown'),
            last_seen = COALESCE(last_seen, NULL)
        WHERE agent_type IS NULL 
           OR connection IS NULL 
           OR capabilities IS NULL 
           OR status IS NULL
    """)
    
    updated = cursor.rowcount
    print(f"[UPDATE] Updated {updated} agent records")
    
    conn.commit()
    conn.close()
    
    print("[DONE] Data update completed!")

if __name__ == "__main__":
    update_old_data()
