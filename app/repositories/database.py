"""
Database configuration and connection manager for Sentinel.
Handles database connections (MariaDB with SQLite support) and initial schema provisioning.
"""

import os
import sqlite3
from typing import Optional, Any
import pymysql
import pymysql.cursors


class DatabaseConnection:
    """
    Manages database connections (MariaDB or SQLite) and table lifecycle.
    Encapsulates connection creation and schema initialization.
    """

    def __init__(
        self,
        db_type: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: Optional[str] = None,
        db_path: Optional[str] = None
    ):
        """
        Initialize database connection manager.
        
        :param db_type: Type of database ('mariadb' or 'sqlite'). Defaults to 'mariadb'.
        :param host: MariaDB host (defaults to DB_HOST env or '127.0.0.1').
        :param port: MariaDB port (defaults to DB_PORT env or 3306).
        :param user: MariaDB user (defaults to DB_USER env or 'root').
        :param password: MariaDB password (defaults to DB_PASSWORD env or '1234').
        :param database: MariaDB database name (defaults to DB_NAME env or 'sentinel').
        :param db_path: Path to SQLite database file if using SQLite.
        """
        # Determine database type
        if db_type:
            self._db_type = db_type.lower()
        elif db_path and not host and not os.environ.get("DB_HOST"):
            self._db_type = "sqlite"
        else:
            self._db_type = os.environ.get("DB_TYPE", "mariadb").lower()

        # MariaDB configuration
        self._host = host or os.environ.get("DB_HOST", "127.0.0.1")
        self._port = int(port or os.environ.get("DB_PORT", 3306))
        self._user = user or os.environ.get("DB_USER", "root")
        self._password = password or os.environ.get("DB_PASSWORD", "1234")
        self._database = database or os.environ.get("DB_NAME", "sentinel")

        # SQLite fallback configuration
        self._db_path = db_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "sentinel.db"
        )

    @property
    def db_type(self) -> str:
        """Get the current database type ('mariadb' or 'sqlite')."""
        return self._db_type

    @property
    def db_path(self) -> str:
        """Get the current SQLite database path."""
        return self._db_path

    def get_connection(self) -> Any:
        """
        Create and return an active database connection.
        - For MariaDB: returns pymysql.Connection with DictCursor for dictionary-like column access.
        - For SQLite: returns sqlite3.Connection with Row row factory.
        
        :return: Connection object (PyMySQL or SQLite)
        """
        if self._db_type == "mariadb":
            return pymysql.connect(
                host=self._host,
                port=self._port,
                user=self._user,
                password=self._password,
                database=self._database,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )
        else:
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

            if self._db_type == "mariadb":
                # MariaDB schema
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(100) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        role VARCHAR(50) NOT NULL DEFAULT 'analyst',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS incidents (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        title VARCHAR(255) NOT NULL,
                        description TEXT NOT NULL,
                        severity VARCHAR(50) NOT NULL,
                        source_url TEXT,
                        source_title VARCHAR(255),
                        attachment_filename VARCHAR(255),
                        created_by VARCHAR(100) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS comments (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        incident_id INT NOT NULL,
                        user_id INT NOT NULL,
                        username VARCHAR(100) NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT fk_comments_incident FOREIGN KEY (incident_id) REFERENCES incidents (id) ON DELETE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """)
            else:
                # SQLite schema
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL DEFAULT 'analyst',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)

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
