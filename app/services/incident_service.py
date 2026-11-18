"""
Incident management business logic service for Sentinel.
Coordinates incident lifecycle, comments, searches, link previews, and file attachments.
"""

import os
from typing import List, Optional, Tuple
from app.repositories.base import IIncidentRepository, ICommentRepository
from app.models.incident import Incident
from app.models.comment import Comment
from app.services.preview_service import PreviewService


class IncidentService:
    """
    Service coordinating incident creation, retrieval, search, comments, and attachments.
    """

    def __init__(
        self,
        incident_repo: IIncidentRepository,
        comment_repo: ICommentRepository,
        preview_service: Optional[PreviewService] = None
    ):
        """
        Initialize IncidentService.
        
        :param incident_repo: IIncidentRepository implementation
        :param comment_repo: ICommentRepository implementation
        :param preview_service: PreviewService instance for external URL metadata fetching
        """
        self._incident_repo = incident_repo
        self._comment_repo = comment_repo
        self._preview_service = preview_service or PreviewService()

    def create_incident(
        self,
        title: str,
        description: str,
        severity: str,
        created_by: str,
        source_url: Optional[str] = None,
        attachment_file = None,
        upload_folder: str = "app/static/uploads",
        status: str = "New",
        assigned_to: Optional[str] = None
    ) -> Incident:
        """
        Create and persist a new security incident.
        
        :param title: Incident title
        :param description: Incident description
        :param severity: Severity level string
        :param created_by: Creator username
        :param source_url: Optional external intelligence URL
        :param attachment_file: Optional Werkzeug FileStorage object
        :param upload_folder: Target directory path for file attachments
        :param status: Incident status ('New', 'Assigned to', 'Resolved')
        :param assigned_to: Assigned analyst username
        :return: Persisted Incident entity
        """
        source_title = None
        if source_url and source_url.strip():
            source_title = self._preview_service.fetch_source_title(source_url)

        attachment_filename = None
        if attachment_file and hasattr(attachment_file, "filename") and attachment_file.filename:
            raw_filename = os.path.basename(attachment_file.filename)
            os.makedirs(upload_folder, exist_ok=True)
            destination = os.path.join(upload_folder, raw_filename)
            attachment_file.save(destination)
            attachment_filename = raw_filename

        incident = Incident(
            title=title,
            description=description,
            severity=severity,
            created_by=created_by,
            source_url=source_url,
            source_title=source_title,
            attachment_filename=attachment_filename,
            status=status,
            assigned_to=assigned_to
        )
        return self._incident_repo.save(incident)

    def list_incidents(
        self,
        search_term: Optional[str] = None,
        severity_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> List[Incident]:
        """
        List incidents matching search term, severity, status, and creator filters.
        Results are returned ordered most recent first.
        
        :param search_term: Substring filter for title/description
        :param severity_filter: Target severity level
        :param status_filter: Target status ('New', 'Assigned to', 'Resolved')
        :param created_by: Creator filter (e.g. for employees seeing only their own incidents)
        :return: List of Incident entities
        """
        return self._incident_repo.search_and_filter(
            search_term=search_term,
            severity=severity_filter,
            status=status_filter,
            created_by=created_by
        )

    def update_incident_status_and_assignee(
        self,
        incident_id: int,
        status: str,
        assigned_to: Optional[str] = None
    ) -> Optional[Incident]:
        """
        Update the status and assigned analyst of an incident.
        
        :param incident_id: Incident primary key
        :param status: New status ('New', 'Assigned to', 'Resolved')
        :param assigned_to: Optional analyst username assigned
        :return: Updated Incident or None
        """
        incident = self._incident_repo.get_by_id(incident_id)
        if not incident:
            return None
        incident.status = status
        incident.assigned_to = assigned_to if status == "Assigned to" else (assigned_to or None)
        return self._incident_repo.save(incident)

    def delete_incident(self, incident_id: int) -> bool:
        """
        Delete an incident by ID.
        
        :param incident_id: Incident primary key
        :return: True if successfully deleted, False otherwise
        """
        return self._incident_repo.delete(incident_id)

    def get_incident_by_id(self, incident_id: int) -> Optional[Incident]:
        """
        Retrieve incident domain entity by ID.
        
        :param incident_id: Incident primary key
        :return: Incident domain entity or None
        """
        return self._incident_repo.get_by_id(incident_id)

    def get_incident_details(self, incident_id: int) -> Tuple[Optional[Incident], List[Comment]]:
        """
        Retrieve an incident along with all associated investigation comments.
        
        :param incident_id: Incident identifier
        :return: Tuple of (Incident domain instance, List of Comment domain instances)
        """
        incident = self._incident_repo.get_by_id(incident_id)
        if not incident:
            return None, []
        comments = self._comment_repo.get_by_incident_id(incident_id)
        return incident, comments

    def add_comment(
        self,
        incident_id: int,
        user_id: int,
        username: str,
        content: str
    ) -> Comment:
        """
        Post a new investigation comment to an incident.
        
        NOTE (R19 Shortcut): Content is accepted and stored as raw text/HTML without
        sanitization or stripping malicious tags.
        
        :param incident_id: Incident primary key
        :param user_id: Author user ID
        :param username: Author username
        :param content: Raw comment content
        :return: Persisted Comment entity
        """
        comment = Comment(
            incident_id=incident_id,
            user_id=user_id,
            username=username,
            content=content
        )
        return self._comment_repo.save(comment)
