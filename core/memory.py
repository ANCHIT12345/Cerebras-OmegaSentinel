"""Institutional Memory — SQLite store of incidents."""
import sqlite3
from datetime import datetime
from typing import List, Dict


class InstitutionalMemory:
    def __init__(self, db_path: str = "sentinel_memory.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                scenario TEXT,
                final_strategy TEXT,
                tech_score INTEGER,
                culture_score INTEGER,
                economic_score INTEGER,
                temporal_score INTEGER,
                net_impact REAL,
                overall REAL
            )
            """
        )
        self.conn.commit()

    def save(self, scenario: str, strategy: str, critique, net_impact: float) -> None:
        self.conn.execute(
            "INSERT INTO incidents (timestamp, scenario, final_strategy, tech_score, culture_score, economic_score, temporal_score, net_impact, overall) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                datetime.now().isoformat(), scenario[:500], strategy[:2000],
                critique.technical_soundness, critique.cultural_sensitivity,
                critique.economic_optimality, critique.temporal_sustainability,
                net_impact, critique.overall_score,
            ),
        )
        self.conn.commit()

    def search_similar(self, scenario: str, limit: int = 1) -> List[Dict]:
        try:
            cursor = self.conn.execute(
                "SELECT * FROM incidents WHERE scenario LIKE ? ORDER BY overall DESC LIMIT ?",
                (f"%{scenario[:60]}%", limit),
            )
            rows = cursor.fetchall()
            if not rows:
                return []
            return [{"resolution": r[3], "effectiveness": r[9]} for r in rows]
        except Exception:
            return []

    def list_all(self, limit: int = 5) -> List[Dict]:
        try:
            cursor = self.conn.execute(
                "SELECT id, timestamp, scenario, overall FROM incidents ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            rows = cursor.fetchall()
            return [{"id": r[0], "timestamp": r[1], "scenario": r[2], "overall": r[3]} for r in rows]
        except Exception:
            return []