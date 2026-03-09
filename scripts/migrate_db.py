"""
数据库迁移脚本
升级数据库 schema 到最新版本
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "silicon_world.db"

def migrate():
    """执行数据库迁移"""
    
    print(f"[MIGRATE] Starting database migration: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查 agents 表的字段
    cursor.execute("PRAGMA table_info(agents)")
    columns = {row[1] for row in cursor.fetchall()}
    
    print(f"[SCHEMA] Current agents columns: {columns}")
    
    # 需要添加的新字段
    new_columns = {
        "agent_type": "ALTER TABLE agents ADD COLUMN agent_type TEXT DEFAULT 'native'",
        "connection": "ALTER TABLE agents ADD COLUMN connection JSON DEFAULT '{}'",
        "capabilities": "ALTER TABLE agents ADD COLUMN capabilities JSON DEFAULT '[]'",
        "status": "ALTER TABLE agents ADD COLUMN status TEXT DEFAULT 'unknown'",
        "last_seen": "ALTER TABLE agents ADD COLUMN last_seen DATETIME",
    }
    
    # 添加缺失的字段
    for col_name, sql in new_columns.items():
        if col_name not in columns:
            print(f"[ADD] Adding column: {col_name}")
            cursor.execute(sql)
        else:
            print(f"[OK] Column exists: {col_name}")
    
    # 检查 memories 表
    cursor.execute("PRAGMA table_info(memories)")
    memory_columns = {row[1] for row in cursor.fetchall()}
    
    print(f"\n[SCHEMA] Current memories columns: {memory_columns}")
    
    # memories 表需要添加的字段
    memory_new_columns = {
        "embedding": "ALTER TABLE memories ADD COLUMN embedding JSON DEFAULT '[]'",
        "metadata": "ALTER TABLE memories ADD COLUMN metadata JSON DEFAULT '{}'",
    }
    
    for col_name, sql in memory_new_columns.items():
        if col_name not in memory_columns:
            print(f"[ADD] Adding column: {col_name}")
            cursor.execute(sql)
        else:
            print(f"[OK] Column exists: {col_name}")
    
    # 提交更改
    conn.commit()
    conn.close()
    
    print("\n[MIGRATE] Database migration completed!")
    print("[INFO] You can now restart the API service")

if __name__ == "__main__":
    migrate()
