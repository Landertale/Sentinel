"""
Domain entity representing a Security Incident in the Sentinel platform.
"""

from typing import Optional


class Incident:
    """
    Domain model representing a security incident logged in Sentinel.
    Encapsulates incident metadata, severity level, preview data, and attachments.
    """

    SEVERITY_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def __init__(
        self,
        title: str,
        description: str,
        severity: str,
        created_by: str,
        incident_id: Optional[int] = None,
        source_url: Optional[str] = None,
        source_title: Optional[str] = None,
        attachment_filename: Optional[str] = None,
        created_at: Optional[str] = None
    ):
        """
        Initialize an Incident entity.
        
        :param title: Summary title of the security incident
        :param description: Detailed incident report / timeline
        :param severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL)
        :param created_by: Username of the analyst who reported the incident
        :param incident_id: Database unique identifier
        :param source_url: Optional external link / threat intel reference
        :param source_title: Extracted HTML title from external link preview
        :param attachment_filename: Filename of an uploaded log or artifact
        :param created_at: Timestamp of incident creation
        """
        self._id = incident_id
        self._title = title
        self._description = description
        self._severity = (severity or "MEDIUM").upper()
        self._created_by = created_by
        self._source_url = source_url
        self._source_title = source_title
        self._attachment_filename = attachment_filename
        self._created_at = created_at

    # --- Properties and Accessors ---

    @property
    def id(self) -> Optional[int]:
        """Get incident ID."""
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        """Set incident ID after persistence."""
        self._id = value

    @property
    def title(self) -> str:
        """Get incident title."""
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        """Update incident title."""
        self._title = value

    @property
    def description(self) -> str:
        """Get incident description."""
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        """Update incident description."""
        self._description = value

    @property
    def severity(self) -> str:
        """Get incident severity rating."""
        return self._severity

    @severity.setter
    def severity(self, value: str) -> None:
        """Set incident severity rating."""
        self._severity = value.upper()

    @property
    def created_by(self) -> str:
        """Get username of incident creator."""
        return self._created_by

    @property
    def source_url(self) -> Optional[str]:
        """Get source intelligence reference URL."""
        return self._source_url

    @source_url.setter
    def source_url(self, value: Optional[str]) -> None:
        """Set source intelligence reference URL."""
        self._source_url = value

    @property
    def source_title(self) -> Optional[str]:
        """Get extracted title of source intelligence reference."""
        return self._source_title

    @source_title.setter
    def source_title(self, value: Optional[str]) -> None:
        """Set extracted title of source intelligence reference."""
        self._source_title = value

    @property
    def attachment_filename(self) -> Optional[str]:
        """Get uploaded attachment filename."""
        return self._attachment_filename

    @attachment_filename.setter
    def attachment_filename(self, value: Optional[str]) -> None:
        """Set attachment filename."""
        self._attachment_filename = value

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
        Convert incident instance to dictionary.
        
        :return: Dict representation of incident data
        """
        return {
            "id": self._id,
            "title": self._title,
            "description": self._description,
            "severity": self._severity,
            "created_by": self._created_by,
            "source_url": self._source_url,
            "source_title": self._source_title,
            "attachment_filename": self._attachment_filename,
            "created_at": self._created_at
        }
