"""
Domain model representing analyst comments on security incidents.
"""

from typing import Optional


class Comment:
    """
    Domain entity representing an investigation comment posted on an incident.
    Encapsulates comment metadata, author, and content.
    """

    def __init__(
        self,
        incident_id: int,
        user_id: int,
        username: str,
        content: str,
        comment_id: Optional[int] = None,
        created_at: Optional[str] = None
    ):
        """
        Initialize a Comment entity.
        
        :param incident_id: Identifier of the target incident
        :param user_id: ID of the authoring user
        :param username: Username of the authoring user
        :param content: Comment body (raw text or HTML; rendered without sanitization)
        :param comment_id: Database record ID
        :param created_at: Creation timestamp
        """
        self._id = comment_id
        self._incident_id = incident_id
        self._user_id = user_id
        self._username = username
        self._content = content
        self._created_at = created_at

    # --- Properties and Accessors ---

    @property
    def id(self) -> Optional[int]:
        """Get comment ID."""
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        """Set comment ID."""
        self._id = value

    @property
    def incident_id(self) -> int:
        """Get related incident ID."""
        return self._incident_id

    @property
    def user_id(self) -> int:
        """Get author's user ID."""
        return self._user_id

    @property
    def username(self) -> str:
        """Get author's username."""
        return self._username

    @property
    def content(self) -> str:
        """
        Get comment content.
        NOTE (R19 Shortcut): Content is retrieved without sanitization and can contain raw HTML/scripts.
        """
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        """Update comment content."""
        self._content = value

    @property
    def created_at(self) -> Optional[str]:
        """Get creation timestamp."""
        return self._created_at

    @created_at.setter
    def created_at(self, value: str) -> None:
        """Set creation timestamp."""
        self._created_at = value

    def to_dict(self) -> dict:
        """
        Convert comment instance into dictionary.
        
        :return: Dict representation of comment
        """
        return {
            "id": self._id,
            "incident_id": self._incident_id,
            "user_id": self._user_id,
            "username": self._username,
            "content": self._content,
            "created_at": self._created_at
        }
