"""Database module for persistent metric storage."""
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional

class MetricsDatabase:
    """SQLite database for persistent metric storage."""
    
    def __init__(self, db_path: str = "metrics.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_schema()
    
    def _create_schema(self):
        """Create database tables."""
        self.cursor.execute("""
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
            )
        """)
        self.conn.commit()
    
    def create_metric(self, metric: Dict) -> None:
        """Create a new metric."""
        self.cursor.execute("""
            INSERT INTO metrics VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metric["id"], metric["name"], metric["description"],
            metric["calculation"], metric["owner"], metric.get("data_source"),
            json.dumps(metric.get("tags", [])),
            json.dumps(metric.get("dependencies", [])),
            metric.get("test_count", 0), metric.get("usage_count", 0),
            metric["created_at"], metric["updated_at"]
        ))
        self.conn.commit()
    
    def get_metric(self, metric_id: str) -> Optional[Dict]:
        """Get a metric by ID."""
        self.cursor.execute("SELECT * FROM metrics WHERE id = ?", (metric_id,))
        row = self.cursor.fetchone()
        if row:
            metric = dict(row)
            metric["tags"] = json.loads(metric.get("tags") or "[]")
            metric["dependencies"] = json.loads(metric.get("dependencies") or "[]")
            return metric
        return None
    
    def close(self):
        """Close database connection."""
        self.conn.close()
