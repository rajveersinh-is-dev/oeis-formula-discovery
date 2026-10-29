"""
Transactional checkpointing for full database scans.
Ensures zero data corruption on process interruption.
"""

from pathlib import Path
import sqlite3
from typing import Optional, Set


class ScanCheckpoint:
    def __init__(self, db_conn: sqlite3.Connection):
        self.conn = db_conn

    def get_completed_sequences(self) -> Set[str]:
        """Returns set of all A-numbers already processed."""
        cursor = self.conn.execute("SELECT a_number FROM scan_status WHERE status = 'completed'")
        return {row[0] for row in cursor.fetchall()}

    def record_progress(self, a_num: str, status: str, count: int, error: Optional[str] = None) -> None:
        """Atomic progress update."""
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO scan_status (a_number, status, candidates_count, error_message)
                VALUES (?, ?, ?, ?)
            """, (a_num, status, count, error))

