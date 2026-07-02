import sqlite3
import os
from typing import List, Dict, Any, Optional

class DatabaseConnector:
    """
    Abstract base class for database connections.
    Your teammate can implement this interface for Postgres, MySQL, etc.
    """
    def connect(self):
        raise NotImplementedError
        
    def url_exists(self, url: str) -> bool:
        raise NotImplementedError
        
    def insert_update(self, data: Dict[str, Any]) -> bool:
        raise NotImplementedError
        
    def get_updates(self, limit: int = 50) -> List[Dict[str, Any]]:
        raise NotImplementedError

class LocalSQLiteConnector(DatabaseConnector):
    """
    Local SQLite implementation for the Ultimate Pipeline.
    """
    def __init__(self, db_path: str = "rbi_data.db"):
        self.db_path = db_path
        self._init_db()
        
    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Create the regulatory_updates table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS regulatory_updates (
            id TEXT PRIMARY KEY,
            source TEXT,
            feedKind TEXT,
            channelTitle TEXT,
            title TEXT,
            summary TEXT,
            url TEXT UNIQUE,
            rawPublishedAt TEXT,
            publishedAt TEXT,
            affected_entities TEXT,
            regulatory_impact TEXT,
            raw_text TEXT,
            embedding BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        conn.close()

    def url_exists(self, url: str) -> bool:
        if not url:
            return False
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM regulatory_updates WHERE url = ?", (url,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def insert_update(self, data: Dict[str, Any]) -> bool:
        conn = self._get_conn()
        cursor = conn.cursor()
        try:
            # We extract fields from data, safely defaulting to None or empty string if missing
            cursor.execute('''
            INSERT OR REPLACE INTO regulatory_updates (
                id, source, feedKind, channelTitle, title, summary, url, 
                rawPublishedAt, publishedAt, affected_entities, regulatory_impact, 
                raw_text, embedding
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get("id", ""),
                data.get("source", ""),
                data.get("feedKind", ""),
                data.get("channelTitle", ""),
                data.get("title", ""),
                data.get("summary", ""),
                data.get("url", ""),
                data.get("rawPublishedAt", ""),
                data.get("publishedAt", ""),
                ", ".join(data.get("affected_entities", [])), # Store lists as comma separated for now
                data.get("regulatory_impact", ""),
                data.get("raw_text", ""),
                data.get("embedding", None) # BLOB
            ))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # URL might already exist if racing
            return False
        except Exception as e:
            print(f"[!] Database insert error: {e}")
            return False
        finally:
            conn.close()

    def get_updates(self, limit: int = 50) -> List[Dict[str, Any]]:
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute('''
        SELECT id, source, feedKind, channelTitle, title, summary, url, 
               rawPublishedAt, publishedAt, affected_entities, regulatory_impact, 
               raw_text, created_at, embedding 
        FROM regulatory_updates 
        ORDER BY publishedAt DESC 
        LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
