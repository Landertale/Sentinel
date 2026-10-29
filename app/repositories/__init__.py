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
    SQLiteUserRepository,
    MariaDBUserRepository,
    UserRepository
)
from app.repositories.incident_repository import (
    SQLiteIncidentRepository,
    MariaDBIncidentRepository,
    IncidentRepository
)
from app.repositories.comment_repository import (
    SQLiteCommentRepository,
    MariaDBCommentRepository,
    CommentRepository
)

__all__ = [
    "DatabaseConnection",
    "IBaseRepository",
    "IUserRepository",
    "IIncidentRepository",
    "ICommentRepository",
    "SQLiteUserRepository",
    "SQLiteIncidentRepository",
    "SQLiteCommentRepository",
    "MariaDBUserRepository",
    "MariaDBIncidentRepository",
    "MariaDBCommentRepository",
    "UserRepository",
    "IncidentRepository",
    "CommentRepository"
]
