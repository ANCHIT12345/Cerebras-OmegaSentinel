"""Scenario Library — search 10k+ scenarios in SQLite."""
import os
import sqlite3
from typing import List, Dict, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "scenarios.db")


class ScenarioLibrary:
    def __init__(self):
        # Fallback JSON if DB doesn't exist yet
        self.json_path = os.path.join(HERE, "scenarios.json")
        self._db_exists = os.path.exists(DB_PATH)
        if not self._db_exists:
            print("[ScenarioLibrary] scenarios.db not found. Run: python data/generate_scenarios.py")

    @property
    def total(self) -> int:
        if not self._db_exists:
            return 0
        conn = sqlite3.connect(DB_PATH)
        n = conn.execute("SELECT COUNT(*) FROM scenarios").fetchone()[0]
        conn.close()
        return n

    def search(self, query: str = "", limit: int = 50) -> List[Dict]:
        """Search scenarios. Empty query returns highest-severity first."""
        if not self._db_exists:
            return self._json_fallback()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        if not query.strip():
            rows = conn.execute(
                "SELECT * FROM scenarios ORDER BY severity ASC, id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            # Split into terms, AND-match each term across all columns
            terms = [t for t in query.split() if t.strip()]
            if not terms:
                rows = conn.execute(
                    "SELECT * FROM scenarios ORDER BY severity ASC, id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
            else:
                clauses = []
                params: list = []
                cols = ("title", "context", "sector", "crisis_type", "region", "severity", "time_context")
                for term in terms:
                    q = f"%{term}%"
                    clause = "(" + " OR ".join([f"{c} LIKE ?" for c in cols]) + ")"
                    clauses.append(clause)
                    params.extend([q] * len(cols))
                where = " AND ".join(clauses)
                sql = (f"SELECT * FROM scenarios WHERE {where} "
                       "ORDER BY CASE severity WHEN 'SEV-1' THEN 0 WHEN 'SEV-2' THEN 1 ELSE 2 END, id DESC LIMIT ?")
                params.append(limit)
                rows = conn.execute(sql, params).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_by_id(self, scenario_id: int) -> Optional[Dict]:
        if not self._db_exists:
            return None
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM scenarios WHERE id = ?", (scenario_id,)).fetchone()
        conn.close()
        return dict(row) if row else None

    def sectors(self) -> List[str]:
        if not self._db_exists:
            return []
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("SELECT DISTINCT sector FROM scenarios ORDER BY sector").fetchall()
        conn.close()
        return [r[0] for r in rows]

    def regions(self) -> List[str]:
        if not self._db_exists:
            return []
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute("SELECT DISTINCT region FROM scenarios ORDER BY region").fetchall()
        conn.close()
        return [r[0] for r in rows]

    def _json_fallback(self) -> List[Dict]:
        import json
        if not os.path.exists(self.json_path):
            return []
        with open(self.json_path) as f:
            raw = json.load(f)
        return [{"id": k, "title": k, "context": v["context"], "sector": "fallback",
                 "crisis_type": "", "region": "", "severity": "", "time_context": "",
                 "image_keys": ",".join(v.get("suggested_image_keys", []))}
                for k, v in raw.items()]