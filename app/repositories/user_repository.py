"""
Concrete SQLite implementation of IUserRepository.
Handles persistence and retrieval of User entities using direct SQLite queries.
"""

from typing import List, Optional
from app.repositories.base import IUserRepository
from app.repositories.database import DatabaseConnection
from app.models.user import User, user_factory


class SQLiteUserRepository(IUserRepository):
    """
    SQLite implementation of the User repository.
    NOTE (R19 Shortcut): Executes string-built raw SQL queries without parameterized inputs
    and handles passwords in plain text per rapid prototype constraints.
    """

    def __init__(self, db: DatabaseConnection):
        """
        Initialize the SQLiteUserRepository.
        
        :param db: DatabaseConnection instance providing active database access.
        """
        self._db = db

    def get_by_id(self, entity_id: int) -> Optional[User]:
        """
        Fetch a user by numeric primary key.
        
        :param entity_id: User identifier
        :return: Domain User instance or None
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        # Raw query execution
        query = f"SELECT id, username, password, role FROM users WHERE id = {entity_id}"
        cursor.execute(query)
        row = cursor.fetchone()
        conn.close()

        if row:
            return user_factory(
                username=row["username"],
                password=row["password"],
                role=row["role"],
                user_id=row["id"]
            )
        return None

    def get_by_username(self, username: str) -> Optional[User]:
        """
        Fetch a user by exact username.
        
        NOTE (R19 Shortcut): String-built raw SQL query without parameterization.
        This intentionally trusts input and demonstrates SQL injection exposure.
        
        :param username: Target username string
        :return: Domain User instance or None
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        
        # Directly string-interpolated query (intentional shortcut)
        query = f"SELECT id, username, password, role FROM users WHERE username = '{username}'"
        cursor.execute(query)
        row = cursor.fetchone()
        conn.close()

        if row:
            return user_factory(
                username=row["username"],
                password=row["password"],
                role=row["role"],
                user_id=row["id"]
            )
        return None

    def get_all(self) -> List[User]:
        """
        Retrieve all registered users.
        
        :return: List of all domain User instances
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password, role FROM users ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()

        return [
            user_factory(
                username=row["username"],
                password=row["password"],
                role=row["role"],
                user_id=row["id"]
            )
            for row in rows
        ]

    def save(self, entity: User) -> User:
        """
        Persist a new or existing User entity.
        
        NOTE (R19 Shortcut): Stores passwords directly in plain text and executes
        raw SQL query string without escaping or sanitizing inputs.
        
        :param entity: Domain User entity to save
        :return: User entity with assigned ID
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        if entity.id is None:
            # Insert new user with plain text password
            query = (
                f"INSERT INTO users (username, password, role) "
                f"VALUES ('{entity.username}', '{entity.password}', '{entity.role}')"
            )
            cursor.execute(query)
            conn.commit()
            entity.id = cursor.lastrowid
        else:
            # Update existing user
            query = (
                f"UPDATE users SET username = '{entity.username}', "
                f"password = '{entity.password}', role = '{entity.role}' "
                f"WHERE id = {entity.id}"
            )
            cursor.execute(query)
            conn.commit()

        conn.close()
        return entity

    def delete(self, entity_id: int) -> bool:
        """
        Delete a user record by primary key.
        
        :param entity_id: Target user ID
        :return: True if record was deleted, False otherwise
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        query = f"DELETE FROM users WHERE id = {entity_id}"
        cursor.execute(query)
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted
