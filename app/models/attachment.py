"""
Domain model representing file attachments linked to incidents.
"""

from typing import Optional


class Attachment:
    """
    Domain entity representing an uploaded artifact, pcap, or log file.
    Encapsulates file attributes and local storage paths.
    """

    def __init__(
        self,
        filename: str,
        file_path: str,
        incident_id: Optional[int] = None,
        file_size: Optional[int] = None
    ):
        """
        Initialize an Attachment entity.
        
        :param filename: Stored filename on the filesystem (unsanitized per prototype shortcut)
        :param file_path: Absolute or relative system path to stored file
        :param incident_id: Linked incident ID
        :param file_size: Size in bytes if calculated
        """
        self._filename = filename
        self._file_path = file_path
        self._incident_id = incident_id
        self._file_size = file_size

    # --- Properties and Accessors ---

    @property
    def filename(self) -> str:
        """Get filename."""
        return self._filename

    @property
    def file_path(self) -> str:
        """Get file path."""
        return self._file_path

    @property
    def incident_id(self) -> Optional[int]:
        """Get linked incident ID."""
        return self._incident_id

    @property
    def file_size(self) -> Optional[int]:
        """Get file size in bytes."""
        return self._file_size

    def to_dict(self) -> dict:
        """
        Convert attachment to dictionary representation.
        
        :return: Dict of attachment attributes
        """
        return {
            "filename": self._filename,
            "file_path": self._file_path,
            "incident_id": self._incident_id,
            "file_size": self._file_size
        }
