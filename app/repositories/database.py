"""
Database configuration and SQLite connection manager for Sentinel.
Handles database connections and initial schema provisioning.
"""

import sqlite3
import os
from typing import Optional


class DatabaseConnection:
    """
    Manages SQLite database connections and table lifecycle.
    Encapsulates connection creation and schema initialization.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection manager.
        
        :param db_path: Path to the SQLite database file. Defaults to sentinel.db in workspace root.
        """
        self._db_path = db_path or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "sentinel.db")

    @property
    def db_path(self) -> str:
        """Get the current database path."""
        return self._db_path

    def get_connection(self) -> sqlite3.Connection:
        """
        Create and return a raw SQLite database connection.
        Enables row factory for dictionary-like column access.
        
        :return: sqlite3.Connection object
        """
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """
        Initialize database schema by creating necessary tables if they do not exist.
        Sets up users, incidents, and comments tables.
        """
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Users table: plain text passwords stored as per intentional prototype constraint
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'analyst',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Incidents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    source_url TEXT,
                    source_title TEXT,
                    attachment_filename TEXT,
                    created_by TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Comments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (incident_id) REFERENCES incidents (id) ON DELETE CASCADE
                );
            """)
            conn.commit()
        finally:
            conn.close()
