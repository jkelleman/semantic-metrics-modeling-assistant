"""SQLite persistence for metric definitions, change history, validation tests, usage and trust scores."""
import json
import sqlite3
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

# Fields a caller may change with update_metric. List fields are stored as JSON.
_UPDATABLE = {"name", "description", "calculation", "owner", "data_source", "tags", "dependencies", "test_count", "usage_count"}
_JSON_FIELDS = {"tags", "dependencies"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class MetricsDatabase:
    """A five-table store: metrics, metric_history, validation_tests, usage_events and trust_scores."""

    def __init__(self, db_path: str = "metrics.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_schema()

    def _create_schema(self):
        self.cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS metrics (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                calculation TEXT,
                owner TEXT,
                data_source TEXT,
                tags TEXT,
                dependencies TEXT,
                test_count INTEGER DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                created_at TEXT,
                updated_at TEXT
            );
            CREATE TABLE IF NOT EXISTS metric_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_id TEXT NOT NULL,
                field_name TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                changed_by TEXT,
                changed_at TEXT
            );
            CREATE TABLE IF NOT EXISTS validation_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_id TEXT NOT NULL,
                test_type TEXT,
                test_query TEXT,
                expected_result TEXT,
                status TEXT,
                created_at TEXT
            );
            CREATE TABLE IF NOT EXISTS usage_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_id TEXT NOT NULL,
                consumer_id TEXT,
                consumer_name TEXT,
                used_at TEXT
            );
            CREATE TABLE IF NOT EXISTS trust_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_id TEXT NOT NULL,
                score REAL NOT NULL,
                breakdown TEXT,
                recorded_at TEXT
            );
            """
        )
        self.conn.commit()

    # Metrics ---------------------------------------------------------------

    def _row_to_metric(self, row: sqlite3.Row) -> Dict[str, Any]:
        metric = dict(row)
        for field in _JSON_FIELDS:
            metric[field] = json.loads(metric.get(field) or "[]")
        return metric

    def create_metric(self, metric: Dict) -> str:
        """Create a metric and return its ID. Timestamps default to now."""
        now = _now()
        self.cursor.execute(
            "INSERT INTO metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                metric["id"], metric["name"], metric.get("description"),
                metric.get("calculation"), metric.get("owner"), metric.get("data_source"),
                json.dumps(metric.get("tags", [])), json.dumps(metric.get("dependencies", [])),
                metric.get("test_count", 0), metric.get("usage_count", 0),
                metric.get("created_at", now), metric.get("updated_at", now),
            ),
        )
        self.conn.commit()
        return metric["id"]

    def get_metric(self, metric_id: str) -> Optional[Dict]:
        """Get a metric by ID, or None."""
        self.cursor.execute("SELECT * FROM metrics WHERE id = ?", (metric_id,))
        row = self.cursor.fetchone()
        return self._row_to_metric(row) if row else None

    def get_all_metrics(self) -> List[Dict]:
        self.cursor.execute("SELECT * FROM metrics ORDER BY name")
        return [self._row_to_metric(r) for r in self.cursor.fetchall()]

    def update_metric(self, metric_id: str, updates: Dict, changed_by: str = "unknown") -> None:
        """Update fields on a metric and record one history row per changed field."""
        current = self.get_metric(metric_id)
        if current is None:
            raise KeyError(f"Metric '{metric_id}' not found")
        now = _now()
        for field, value in updates.items():
            if field not in _UPDATABLE:
                raise ValueError(f"Field '{field}' can't be updated")
            old = current.get(field)
            if old == value:
                continue
            stored = json.dumps(value) if field in _JSON_FIELDS else value
            self.cursor.execute(f"UPDATE metrics SET {field} = ?, updated_at = ? WHERE id = ?", (stored, now, metric_id))
            self.cursor.execute(
                "INSERT INTO metric_history (metric_id, field_name, old_value, new_value, changed_by, changed_at) VALUES (?, ?, ?, ?, ?, ?)",
                (metric_id, field, json.dumps(old), json.dumps(value), changed_by, now),
            )
        self.conn.commit()

    def delete_metric(self, metric_id: str) -> None:
        """Delete a metric and everything recorded about it."""
        for table in ("metric_history", "validation_tests", "usage_events", "trust_scores"):
            self.cursor.execute(f"DELETE FROM {table} WHERE metric_id = ?", (metric_id,))
        self.cursor.execute("DELETE FROM metrics WHERE id = ?", (metric_id,))
        self.conn.commit()

    # Search ----------------------------------------------------------------

    def search_metrics(self, query: str) -> List[Dict]:
        """Case-insensitive match on name or description."""
        like = f"%{query}%"
        self.cursor.execute(
            "SELECT * FROM metrics WHERE name LIKE ? OR description LIKE ? ORDER BY name", (like, like)
        )
        return [self._row_to_metric(r) for r in self.cursor.fetchall()]

    def get_metrics_by_owner(self, owner: str) -> List[Dict]:
        self.cursor.execute("SELECT * FROM metrics WHERE owner = ? ORDER BY name", (owner,))
        return [self._row_to_metric(r) for r in self.cursor.fetchall()]

    def get_metrics_by_tag(self, tag: str) -> List[Dict]:
        return [m for m in self.get_all_metrics() if tag in m["tags"]]

    # History, tests and usage ---------------------------------------------

    def get_metric_history(self, metric_id: str, limit: int = 50) -> List[Dict]:
        """Change history, oldest first."""
        self.cursor.execute(
            "SELECT * FROM metric_history WHERE metric_id = ? ORDER BY id LIMIT ?", (metric_id, limit)
        )
        rows = []
        for r in self.cursor.fetchall():
            row = dict(r)
            row["old_value"] = json.loads(row["old_value"]) if row["old_value"] is not None else None
            row["new_value"] = json.loads(row["new_value"]) if row["new_value"] is not None else None
            rows.append(row)
        return rows

    def add_validation_test(self, metric_id: str, test: Dict) -> int:
        self.cursor.execute(
            "INSERT INTO validation_tests (metric_id, test_type, test_query, expected_result, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (metric_id, test.get("test_type"), test.get("test_query"), test.get("expected_result"), test.get("status"), _now()),
        )
        self.cursor.execute("UPDATE metrics SET test_count = test_count + 1 WHERE id = ?", (metric_id,))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_validation_tests(self, metric_id: str) -> List[Dict]:
        self.cursor.execute("SELECT * FROM validation_tests WHERE metric_id = ? ORDER BY id", (metric_id,))
        return [dict(r) for r in self.cursor.fetchall()]

    def record_usage(self, metric_id: str, consumer_id: str, consumer_name: str = "") -> None:
        self.cursor.execute(
            "INSERT INTO usage_events (metric_id, consumer_id, consumer_name, used_at) VALUES (?, ?, ?, ?)",
            (metric_id, consumer_id, consumer_name, _now()),
        )
        self.cursor.execute("UPDATE metrics SET usage_count = usage_count + 1 WHERE id = ?", (metric_id,))
        self.conn.commit()

    def get_usage_stats(self, metric_id: str) -> Dict[str, Any]:
        self.cursor.execute(
            "SELECT COUNT(*) AS total, COUNT(DISTINCT consumer_id) AS consumers, MAX(used_at) AS last_used FROM usage_events WHERE metric_id = ?",
            (metric_id,),
        )
        r = self.cursor.fetchone()
        return {"total_uses": r["total"], "unique_consumers": r["consumers"], "last_used": r["last_used"]}

    # Trust scores -----------------------------------------------------------

    def record_trust_score(self, metric_id: str, score: float, breakdown: Dict) -> None:
        self.cursor.execute(
            "INSERT INTO trust_scores (metric_id, score, breakdown, recorded_at) VALUES (?, ?, ?, ?)",
            (metric_id, score, json.dumps(breakdown), _now()),
        )
        self.conn.commit()

    def get_trust_score_history(self, metric_id: str, days: int = 30) -> List[Dict]:
        """Trust scores within the last `days` days, most recent first."""
        since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        self.cursor.execute(
            "SELECT * FROM trust_scores WHERE metric_id = ? AND recorded_at >= ? ORDER BY id DESC", (metric_id, since)
        )
        rows = []
        for r in self.cursor.fetchall():
            row = dict(r)
            row["breakdown"] = json.loads(row["breakdown"] or "{}")
            rows.append(row)
        return rows

    def close(self):
        self.conn.close()
