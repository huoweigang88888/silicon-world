#!/usr/bin/env python3
"""
硅基世界 - 自动同步脚本
监控文件变化并自动提交推送到 GitHub
"""

import os
import time
import subprocess
from pathlib import Path
from datetime import datetime

class AutoSync:
    def __init__(self, repo_path: str, interval: int = 60):
        self.repo_path = Path(repo_path)
        self.interval = interval
        self.last_sync = None
    
    def run_command(self, cmd: str) -> str:
        """运行 shell 命令"""
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=self.repo_path
        )
        return result.stdout + result.stderr
    
    def has_changes(self) -> bool:
        """检查是否有更改"""
        output = self.run_command("git status --porcelain")
        return bool(output.strip())
    
    def sync(self):
        """执行同步"""
        if not self.has_changes():
            print(f"[{datetime.now()}] 无更改，跳过")
            return
        
        print(f"[{datetime.now()}] 发现更改，开始同步...")
        
        # git add
        self.run_command("git add -A")
        print("  ✓ 添加文件")
        
        # git commit
        message = f"chore: auto sync at {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        self.run_command(f'git commit -m "{message}"')
        print("  ✓ 提交更改")
        
        # git push
        output = self.run_command("git push -u origin main")
        print("  ✓ 推送到 GitHub")
        
        if "error" in output.lower():
            print(f"  ✗ 推送失败：{output}")
        else:
            print(f"  ✓ 同步成功")
        
        self.last_sync = datetime.now()
    
    def start(self):
        """启动监控"""
        print("=" * 50)
        print("硅基世界 - 自动同步服务")
        print("=" * 50)
        print(f"仓库：{self.repo_path}")
        print(f"间隔：{self.interval}秒")
        print("按 Ctrl+C 停止")
        print("=" * 50)
        
        try:
            while True:
                self.sync()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\n\n停止同步服务")


if __name__ == "__main__":
    repo_path = Path(__file__).parent
    sync = AutoSync(repo_path, interval=300)  # 5 分钟检查一次
    sync.start()
