"""
Repository interfaces for Sentinel data access layer.
Defines Abstract Base Classes (ABCs) specifying the contract for data persistence.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from app.models.user import User
from app.models.incident import Incident
from app.models.comment import Comment

T = TypeVar("T")


class IBaseRepository(ABC, Generic[T]):
    """
    Generic Abstract Base Class defining standard CRUD repository contract.
    Enforces abstraction and dependency inversion across the application.
    """

    @abstractmethod
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """
        Fetch entity by unique identifier.
        
        :param entity_id: Record primary key
        :return: Domain entity instance or None
        """
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """
        Retrieve all entities.
        
        :return: List of domain entities
        """
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        """
        Persist a domain entity.
        
        :param entity: Domain entity to persist
        :return: Persisted entity with updated identifier
        """
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> bool:
        """
        Delete an entity by its identifier.
        
        :param entity_id: Identifier of record to delete
        :return: True if deleted, False otherwise
        """
        pass


class IUserRepository(IBaseRepository[User]):
    """
    Repository interface for User entities.
    """

    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Find a user by username.
        
        :param username: Target username string
        :return: User entity or None
        """
        pass


class IIncidentRepository(IBaseRepository[Incident]):
    """
    Repository interface for Incident entities.
    """

    @abstractmethod
    def search_and_filter(self, search_term: Optional[str] = None, severity: Optional[str] = None) -> List[Incident]:
        """
        Search and filter incidents with substring matching and severity criteria.
        
        :param search_term: Substring to match in title or description
        :param severity: Severity filter (e.g. HIGH, CRITICAL)
        :return: List of filtered Incident entities, ordered by creation date descending
        """
        pass


class ICommentRepository(IBaseRepository[Comment]):
    """
    Repository interface for Comment entities.
    """

    @abstractmethod
    def get_by_incident_id(self, incident_id: int) -> List[Comment]:
        """
        Fetch all comments attached to a specific incident.
        
        :param incident_id: Incident primary key
        :return: List of Comment entities ordered by timestamp
        """
        pass
