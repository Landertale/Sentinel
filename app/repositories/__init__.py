"""
Repository exports for Sentinel data access layer.
"""

from app.repositories.database import DatabaseConnection
from app.repositories.base import (
    IBaseRepository,
    IUserRepository,
    IIncidentRepository,
    ICommentRepository
)
from app.repositories.user_repository import (
    MariaDBUserRepository,
    UserRepository,
    SQLiteUserRepository
)
from app.repositories.incident_repository import (
    MariaDBIncidentRepository,
    IncidentRepository,
    SQLiteIncidentRepository
)
from app.repositories.comment_repository import (
    MariaDBCommentRepository,
    CommentRepository,
    SQLiteCommentRepository
)

__all__ = [
    "DatabaseConnection",
    "IBaseRepository",
    "IUserRepository",
    "IIncidentRepository",
    "ICommentRepository",
    "MariaDBUserRepository",
    "MariaDBIncidentRepository",
    "MariaDBCommentRepository",
    "UserRepository",
    "IncidentRepository",
    "CommentRepository",
    "SQLiteUserRepository",
    "SQLiteIncidentRepository",
    "SQLiteCommentRepository"
]
