import sqlite3
import os
import time
from typing import List, Dict, Optional

class NexusMemory:
    """
    Persistence layer for short-term conversation and long-term user context.
    """
    def __init__(self, db_path: str = "data/nexus.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation (
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp REAL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    user_id TEXT,
                    fact TEXT,
                    timestamp REAL
                )
            """)
            conn.commit()

    def add_message(self, session_id: str, role: str, content: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO conversation VALUES (?, ?, ?, ?)",
                         (session_id, role, content, time.time()))

    def get_history(self, session_id: str, k: int = 5) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT role, content FROM conversation WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                                  (session_id, k))
            rows = cursor.fetchall()
            return [{"role": r, "content": c} for r, c in reversed(rows)]

memory = NexusMemory()
