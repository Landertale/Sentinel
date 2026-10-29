"""
Concrete SQLite implementation of ICommentRepository.
Handles persistence and retrieval of analyst investigation comments.
"""

from typing import List, Optional
from app.repositories.base import ICommentRepository
from app.repositories.database import DatabaseConnection
from app.models.comment import Comment


class SQLiteCommentRepository(ICommentRepository):
    """
    SQLite implementation of the Comment repository.
    NOTE (R19 Shortcut): Stores and fetches comments verbatim without sanitization,
    allowing raw HTML/scripts to be stored directly.
    """

    def __init__(self, db: DatabaseConnection):
        """
        Initialize SQLiteCommentRepository.
        
        :param db: DatabaseConnection instance providing active database access.
        """
        self._db = db

    def _row_to_comment(self, row) -> Comment:
        """
        Map a SQLite row to a Comment domain instance.
        
        :param row: sqlite3.Row instance
        :return: Comment domain instance
        """
        return Comment(
            comment_id=row["id"],
            incident_id=row["incident_id"],
            user_id=row["user_id"],
            username=row["username"],
            content=row["content"],
            created_at=str(row["created_at"]) if row["created_at"] is not None else None
        )

    def get_by_id(self, entity_id: int) -> Optional[Comment]:
        """
        Retrieve comment by ID.
        
        :param entity_id: Comment primary key
        :return: Comment domain instance or None
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        query = f"SELECT * FROM comments WHERE id = {entity_id}"
        cursor.execute(query)
        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_comment(row)
        return None

    def get_all(self) -> List[Comment]:
        """
        Retrieve all comments across all incidents.
        
        :return: List of all Comment instances
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM comments ORDER BY created_at ASC")
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_comment(row) for row in rows]

    def get_by_incident_id(self, incident_id: int) -> List[Comment]:
        """
        Retrieve all comments for a specific incident.
        
        :param incident_id: Incident identifier
        :return: List of Comment instances ordered by creation date ascending
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        query = f"SELECT * FROM comments WHERE incident_id = {incident_id} ORDER BY created_at ASC"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_comment(row) for row in rows]

    def save(self, entity: Comment) -> Comment:
        """
        Save a new comment record to the database.
        
        NOTE (R19 Shortcut): Content is not stripped of tags or sanitized.
        
        :param entity: Comment entity to persist
        :return: Comment entity with generated ID
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        content_escaped = entity.content.replace("'", "''")

        if entity.id is None:
            query = (
                f"INSERT INTO comments (incident_id, user_id, username, content) VALUES ("
                f"{entity.incident_id}, {entity.user_id}, '{entity.username}', '{content_escaped}')"
            )
            cursor.execute(query)
            conn.commit()
            entity.id = cursor.lastrowid
        else:
            query = (
                f"UPDATE comments SET content = '{content_escaped}' "
                f"WHERE id = {entity.id}"
            )
            cursor.execute(query)
            conn.commit()

        conn.close()
        return entity

    def delete(self, entity_id: int) -> bool:
        """
        Delete a comment by primary key ID.
        
        :param entity_id: Comment primary key
        :return: True if deleted, False otherwise
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        query = f"DELETE FROM comments WHERE id = {entity_id}"
        cursor.execute(query)
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted


# Aliases for compatibility
MariaDBCommentRepository = SQLiteCommentRepository
CommentRepository = SQLiteCommentRepository
