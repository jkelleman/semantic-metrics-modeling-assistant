
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_trust_history_metric 
            ON trust_score_history(metric_id, recorded_at DESC)
        ''')"""
Database module for persistent metric storage.

Provides SQLite-based storage for metrics with full CRUD operations,
history tracking, and query capabilities.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class MetricsDatabase:
    """SQLite database for persistent metric storage."""
    
    def __init__(self, db_path: str = "metrics.db"):
        """Initialize database connection and create schema."""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_schema()
    
    def _create_schema(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        
        # Main metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                calculation TEXT NOT NULL,
                owner TEXT,
                data_source TEXT,
                tags TEXT,  -- JSON array
                dependencies TEXT,  -- JSON array
                test_count INTEGER DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                trust_score INTEGER DEFAULT 0
            )
        ''')
        
        # Metric history table for tracking changes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metric_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_id TEXT NOT NULL,
                field_name TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                changed_by TEXT,
                changed_at TEXT NOT NULL,
                FOREIGN KEY (metric_id) REFERENCES metrics(id)
            )
        ''')
        
        # Validation tests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS validation_tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_id TEXT NOT NULL,
                test_type TEXT NOT NULL,
                test_query TEXT,
                expected_result TEXT,
                last_run TEXT,
                status TEXT,  -- 'passed', 'failed', 'pending'
                FOREIGN KEY (metric_id) REFERENCES metrics(id)
            )
        ''')
        
        # Usage tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metric_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_id TEXT NOT NULL,
                used_by TEXT,
                used_at TEXT NOT NULL,
                context TEXT,  -- dashboard, report, etc.
                FOREIGN KEY (metric_id) REFERENCES metrics(id)
            )
        ''')
        
                # Trust score history table for trend analysis
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS trust_score_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_id TEXT NOT NULL,
                score REAL NOT NULL,
                breakdown TEXT,  -- JSON with component scores
                recorded_at TEXT NOT NULL,
                FOREIGN KEY (metric_id) REFERENCES metrics(id)
            )
        ''')

        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_owner ON metrics(owner)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_metric ON metric_history(metric_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_usage_metric ON metric_usage(metric_id)')
        
        self.conn.commit()
    
    def create_metric(self, metric_id: str, metric_data: Dict) -> bool:
        """Create a new metric."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO metrics (
                    id, name, description, calculation, owner, data_source,
                    tags, dependencies, test_count, usage_count,
                    created_at, updated_at, trust_score
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metric_id,
                metric_data['name'],
                metric_data['description'],
                metric_data['calculation'],
                metric_data['owner'],
                metric_data['data_source'],
                json.dumps(metric_data['tags']),
                json.dumps(metric_data['dependencies']),
                metric_data['test_count'],
                metric_data['usage_count'],
                metric_data['created_at'],
                metric_data['updated_at'],
                metric_data.get('trust_score', 0)
            ))
            
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_metric(self, metric_id: str) -> Optional[Dict]:
        """Retrieve a metric by ID."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM metrics WHERE id = ?', (metric_id,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_dict(row)
        return None
    
    def get_all_metrics(self) -> Dict[str, Dict]:
        """Retrieve all metrics."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM metrics')
        rows = cursor.fetchall()
        
        return {row['id']: self._row_to_dict(row) for row in rows}
    
    def update_metric(self, metric_id: str, updates: Dict, changed_by: str = "system") -> bool:
        """Update a metric and log changes."""
        current = self.get_metric(metric_id)
        if not current:
            return False
        
        cursor = self.conn.cursor()
        
        # Track changes in history
        for field, new_value in updates.items():
            if field in current and current[field] != new_value:
                cursor.execute('''
                    INSERT INTO metric_history (
                        metric_id, field_name, old_value, new_value, changed_by, changed_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    metric_id,
                    field,
                    str(current[field]),
                    str(new_value),
                    changed_by,
                    datetime.now().isoformat()
                ))
        
        # Build update query dynamically
        set_clauses = []
        values = []
        
        for field, value in updates.items():
            if field in ['tags', 'dependencies'] and isinstance(value, list):
                set_clauses.append(f"{field} = ?")
                values.append(json.dumps(value))
            else:
                set_clauses.append(f"{field} = ?")
                values.append(value)
        
        # Always update updated_at
        set_clauses.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        
        values.append(metric_id)
        
        query = f"UPDATE metrics SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(query, values)
        
        self.conn.commit()
        return True
    
    def delete_metric(self, metric_id: str) -> bool:
        """Delete a metric and its related data."""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('DELETE FROM validation_tests WHERE metric_id = ?', (metric_id,))
            cursor.execute('DELETE FROM metric_usage WHERE metric_id = ?', (metric_id,))
            cursor.execute('DELETE FROM metric_history WHERE metric_id = ?', (metric_id,))
            cursor.execute('DELETE FROM metrics WHERE id = ?', (metric_id,))
            
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception:
            self.conn.rollback()
            return False
    
    def search_metrics(self, query: str) -> List[Dict]:
        """Search metrics by name or description."""
        cursor = self.conn.cursor()
        search_pattern = f"%{query}%"
        
        cursor.execute('''
            SELECT * FROM metrics
            WHERE name LIKE ? OR description LIKE ?
            ORDER BY usage_count DESC, trust_score DESC
        ''', (search_pattern, search_pattern))
        
        return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def add_validation_test(self, metric_id: str, test_type: str, test_query: str, expected_result: str) -> int:
        """Add a validation test for a metric."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO validation_tests (
                metric_id, test_type, test_query, expected_result, status
            ) VALUES (?, ?, ?, ?, ?)
        ''', (metric_id, test_type, test_query, expected_result, 'pending'))
        
        # Update test count
        cursor.execute('''
            UPDATE metrics
            SET test_count = (SELECT COUNT(*) FROM validation_tests WHERE metric_id = ?)
            WHERE id = ?
        ''', (metric_id, metric_id))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def record_usage(self, metric_id: str, used_by: str, context: str = "query"):
        """Record metric usage."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO metric_usage (metric_id, used_by, used_at, context)
            VALUES (?, ?, ?, ?)
        ''', (metric_id, used_by, datetime.now().isoformat(), context))
        
        # Update usage count
        cursor.execute('''
            UPDATE metrics
            SET usage_count = (SELECT COUNT(*) FROM metric_usage WHERE metric_id = ?)
            WHERE id = ?
        ''', (metric_id, metric_id))
        
        self.conn.commit()
    
    def get_metric_history(self, metric_id: str, limit: int = 10) -> List[Dict]:
        """Get change history for a metric."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT * FROM metric_history
            WHERE metric_id = ?
            ORDER BY changed_at DESC
            LIMIT ?
        ''', (metric_id, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_metrics_by_owner(self, owner: str) -> List[Dict]:
        """Get all metrics owned by a specific owner."""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT * FROM metrics WHERE owner = ?', (owner,))
        return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def get_metrics_by_tag(self, tag: str) -> List[Dict]:
        """Get all metrics with a specific tag."""
        cursor = self.conn.cursor()
        
        cursor.execute('SELECT * FROM metrics')
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            metric = self._row_to_dict(row)
            if tag in metric['tags']:
                result.append(metric)
        
        return result
    
    def get_usage_stats(self, metric_id: str, days: int = 30) -> Dict:
        """Get usage statistics for a metric."""
        cursor = self.conn.cursor()
        
        from_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        from_date = from_date.replace(day=from_date.day - days).isoformat()
        
        cursor.execute('''
            SELECT COUNT(*) as total_uses,
                   COUNT(DISTINCT used_by) as unique_users,
                   COUNT(DISTINCT context) as unique_contexts
            FROM metric_usage
            WHERE metric_id = ? AND used_at >= ?
        ''', (metric_id, from_date))
        
        row = cursor.fetchone()
        return dict(row) if row else {'total_uses': 0, 'unique_users': 0, 'unique_contexts': 0}
    
    def record_trust_score(self, metric_id: str, score: float, breakdown: Dict) -> None:
        """Record trust score snapshot for trend analysis."""
        self.cursor.execute('''
            INSERT INTO trust_score_history (metric_id, score, breakdown, recorded_at)
            VALUES (?, ?, ?, ?)
        ''', (metric_id, score, json.dumps(breakdown), datetime.now().isoformat()))
        self.conn.commit()

    def get_trust_score_history(self, metric_id: str, days: int = 90) -> List[Dict]:
        """Get trust score history for trend analysis."""
        from_date = datetime.now().replace(day=datetime.now().day - days).isoformat()
        
        self.cursor.execute('''
            SELECT score, breakdown, recorded_at
            FROM trust_score_history
            WHERE metric_id = ? AND recorded_at >= ?
            ORDER BY recorded_at DESC
        ''', (metric_id, from_date))
        
        results = []
        for row in self.cursor.fetchall():
            result = dict(row)
            if result.get('breakdown'):
                result['breakdown'] = json.loads(result['breakdown'])
            results.append(result)
        
        return results

        def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Convert SQLite row to dictionary with proper type conversions."""
        metric = dict(row)
        
        # Parse JSON fields
        if metric.get('tags'):
            metric['tags'] = json.loads(metric['tags'])
        else:
            metric['tags'] = []
        
        if metric.get('dependencies'):
            metric['dependencies'] = json.loads(metric['dependencies'])
        else:
            metric['dependencies'] = []
        
        return metric
    
    def close(self):
        """Close database connection."""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()



