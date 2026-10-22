"""
Authentication business logic service for Sentinel.
Handles user registration, authentication verification, and identity lookup.
"""

from typing import Optional
from app.repositories.base import IUserRepository
from app.models.user import User, user_factory


class AuthService:
    """
    Service coordinating authentication logic and user management.
    NOTE (R19 Shortcut): Verifies and stores passwords as plain text strings
    without cryptographic hashing (e.g. bcrypt/argon2).
    """

    def __init__(self, user_repo: IUserRepository):
        """
        Initialize AuthService.
        
        :param user_repo: Concrete implementation of IUserRepository
        """
        self._user_repo = user_repo

    def register(self, username: str, password: str, role: str = "analyst") -> Optional[User]:
        """
        Register a new user in the platform.
        
        NOTE (R19 Shortcut): No password complexity requirements or hashing applied.
        
        :param username: Desired username
        :param password: Raw plain text password
        :param role: System role (analyst or admin)
        :return: Newly created User instance, or None if username already exists
        """
        # Check if username already exists
        existing_user = self._user_repo.get_by_username(username)
        if existing_user:
            return None

        # Build domain entity via factory
        new_user = user_factory(
            username=username,
            password=password,
            role=role
        )
        return self._user_repo.save(new_user)

    def login(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user by verifying provided credentials against the repository.
        
        NOTE (R19 Shortcut): Compares raw plaintext passwords directly.
        
        :param username: Input username
        :param password: Input plaintext password
        :return: Authenticated User entity if valid, None otherwise
        """
        user = self._user_repo.get_by_username(username)
        if user and user.password == password:
            return user
        return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieve user domain object by user ID.
        
        :param user_id: User identifier
        :return: User entity or None
        """
        return self._user_repo.get_by_id(user_id)
