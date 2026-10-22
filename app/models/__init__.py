"""
Domain model exports for Sentinel.
Exposes core domain entities for clean layered imports.
"""

from app.models.user import User, Analyst, Admin, user_factory
from app.models.incident import Incident
from app.models.comment import Comment
from app.models.attachment import Attachment

__all__ = [
    "User",
    "Analyst",
    "Admin",
    "user_factory",
    "Incident",
    "Comment",
    "Attachment"
]
