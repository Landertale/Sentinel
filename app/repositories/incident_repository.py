"""
Concrete SQLite implementation of IIncidentRepository.
Handles persistence, search, and retrieval of security incident records.
"""

from typing import List, Optional
from app.repositories.base import IIncidentRepository
from app.repositories.database import DatabaseConnection
from app.models.incident import Incident


class SQLiteIncidentRepository(IIncidentRepository):
    """
    SQLite implementation of the Incident repository.
    NOTE (R19 Shortcut): Search and filtering operations use string interpolation
    in raw SQL statements with zero input validation or escaping.
    """

    def __init__(self, db: DatabaseConnection):
        """
        Initialize the SQLiteIncidentRepository.
        
        :param db: DatabaseConnection instance providing active database access.
        """
        self._db = db

    def _row_to_incident(self, row) -> Incident:
        """
        Helper method to map a SQLite Row into an Incident domain object.
        
        :param row: sqlite3.Row instance
        :return: Incident domain instance
        """
        return Incident(
            incident_id=row["id"],
            title=row["title"],
            description=row["description"],
            severity=row["severity"],
            created_by=row["created_by"],
            source_url=row["source_url"],
            source_title=row["source_title"],
            attachment_filename=row["attachment_filename"],
            created_at=str(row["created_at"]) if row["created_at"] is not None else None
        )

    def get_by_id(self, entity_id: int) -> Optional[Incident]:
        """
        Retrieve an incident by primary key ID.
        
        :param entity_id: Incident identifier
        :return: Incident domain instance or None
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        query = f"SELECT * FROM incidents WHERE id = {entity_id}"
        cursor.execute(query)
        row = cursor.fetchone()
        conn.close()

        if row:
            return self._row_to_incident(row)
        return None

    def get_all(self) -> List[Incident]:
        """
        Retrieve all incidents, ordered most recent first.
        
        :return: List of Incident instances
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        query = "SELECT * FROM incidents ORDER BY created_at DESC, id DESC"
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_incident(row) for row in rows]

    def search_and_filter(self, search_term: Optional[str] = None, severity: Optional[str] = None) -> List[Incident]:
        """
        Search and filter incidents by substring match and severity.
        
        NOTE (R19 Shortcut): Uses direct string formatting / f-strings without sanitization.
        This provides intentional demonstration of raw SQL querying and SQL injection.
        
        :param search_term: Substring to search across title and description
        :param severity: Severity level string (e.g. LOW, MEDIUM, HIGH, CRITICAL)
        :return: Filtered list of Incident entities sorted with most recent first
        """
        conditions = []
        
        if search_term and search_term.strip():
            # Intentional shortcut: unescaped string concatenation
            conditions.append(f"(title LIKE '%{search_term}%' OR description LIKE '%{search_term}%')")

        if severity and severity.strip() and severity.upper() != "ALL":
            conditions.append(f"severity = '{severity.upper()}'")

        query = "SELECT * FROM incidents"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY created_at DESC, id DESC"

        conn = self._db.get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_incident(row) for row in rows]

    def save(self, entity: Incident) -> Incident:
        """
        Save a new or existing Incident entity to the database.
        
        NOTE (R19 Shortcut): Unvalidated string formatting in SQL INSERT/UPDATE.
        
        :param entity: Incident entity
        :return: Incident entity with ID assigned
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()

        # Handle null values for optional fields safely in string format
        source_url_val = f"'{entity.source_url}'" if entity.source_url else "NULL"
        source_title_val = f"'{entity.source_title}'" if entity.source_title else "NULL"
        attachment_val = f"'{entity.attachment_filename}'" if entity.attachment_filename else "NULL"

        # Replace single quotes inside values simply if needed or directly interpolate
        title_val = entity.title.replace("'", "''") if entity.title else ""
        desc_val = entity.description.replace("'", "''") if entity.description else ""

        if entity.id is None:
            query = (
                f"INSERT INTO incidents (title, description, severity, created_by, "
                f"source_url, source_title, attachment_filename) VALUES ("
                f"'{title_val}', '{desc_val}', '{entity.severity}', '{entity.created_by}', "
                f"{source_url_val}, {source_title_val}, {attachment_val})"
            )
            cursor.execute(query)
            conn.commit()
            entity.id = cursor.lastrowid
        else:
            query = (
                f"UPDATE incidents SET title = '{title_val}', description = '{desc_val}', "
                f"severity = '{entity.severity}', source_url = {source_url_val}, "
                f"source_title = {source_title_val}, attachment_filename = {attachment_val} "
                f"WHERE id = {entity.id}"
            )
            cursor.execute(query)
            conn.commit()

        conn.close()
        return entity

    def delete(self, entity_id: int) -> bool:
        """
        Delete an incident by ID.
        
        :param entity_id: Incident primary key
        :return: True if deleted, False otherwise
        """
        conn = self._db.get_connection()
        cursor = conn.cursor()
        query = f"DELETE FROM incidents WHERE id = {entity_id}"
        cursor.execute(query)
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted


# Aliases for compatibility
MariaDBIncidentRepository = SQLiteIncidentRepository
IncidentRepository = SQLiteIncidentRepository
