"""
Authentication business logic service for Sentinel.
Handles user registration, authentication verification, and identity lookup.
Passwords are encrypted using bcrypt.
"""

from typing import List, Optional
import bcrypt
from app.repositories.base import IUserRepository
from app.models.user import User, user_factory


class AuthService:
    """
    Service coordinating authentication logic and user management.
    Passwords are encrypted and verified using bcrypt.
    """

    def __init__(self, user_repo: IUserRepository):
        """
        Initialize AuthService.
        
        :param user_repo: Concrete implementation of IUserRepository
        """
        self._user_repo = user_repo

    def hash_password(self, password: str) -> str:
        """
        Hash plaintext password with bcrypt.
        
        :param password: Raw plain text password
        :return: Bcrypt hash string
        """
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify password against bcrypt hash, with plain text fallback migration.
        
        :param password: Provided plaintext password
        :param hashed_password: Password stored in database
        :return: True if valid, False otherwise
        """
        if not hashed_password:
            return False
        try:
            if hashed_password.startswith(("$2b$", "$2a$", "$2y$")):
                return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
            return password == hashed_password
        except Exception:
            return False

    def register(self, username: str, password: str, role: str = "analyst") -> Optional[User]:
        """
        Register a new user in the platform with a bcrypt hashed password.
        
        :param username: Desired username
        :param password: Raw plain text password
        :param role: System role (analyst, admin, or employee)
        :return: Newly created User instance, or None if username already exists
        """
        # Check if username already exists
        existing_user = self._user_repo.get_by_username(username)
        if existing_user:
            return None

        # Hash password with bcrypt
        encrypted_password = self.hash_password(password)

        # Build domain entity via factory
        new_user = user_factory(
            username=username,
            password=encrypted_password,
            role=role
        )
        return self._user_repo.save(new_user)

    def login(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user by verifying provided credentials against the repository.
        
        :param username: Input username
        :param password: Input plaintext password
        :return: Authenticated User entity if valid, None otherwise
        """
        user = self._user_repo.get_by_username(username)
        if user and self.verify_password(password, user.password):
            # If stored password wasn't bcrypt hashed, upgrade it now
            if not user.password.startswith(("$2b$", "$2a$", "$2y$")):
                user._password = self.hash_password(password)
                self._user_repo.save(user)
            return user
        return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieve user domain object by user ID.
        
        :param user_id: User identifier
        :return: User entity or None
        """
        return self._user_repo.get_by_id(user_id)

    def get_analysts(self) -> List[User]:
        """
        Retrieve all analysts and administrators who can be assigned to incidents.
        
        :return: List of User domain instances with role analyst or admin
        """
        if hasattr(self._user_repo, "get_by_roles"):
            return self._user_repo.get_by_roles(["analyst", "admin"])
        return [u for u in self._user_repo.get_all() if u.role in ("analyst", "admin")]
