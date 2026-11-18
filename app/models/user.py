"""
Domain models representing users in the Sentinel platform.
Demonstrates object-oriented inheritance, encapsulation, and polymorphism.
"""

from typing import Optional


class User:
    """
    Base domain entity representing an authenticated user within Sentinel.
    Encapsulates user credentials and role behaviors.
    """

    def __init__(self, username: str, password: str, role: str = "analyst", user_id: Optional[int] = None):
        """
        Initialize base User entity.
        
        :param username: User account username
        :param password: User password (plain text per prototype shortcut)
        :param role: System role (e.g. analyst, admin)
        :param user_id: Unique database identifier, if persisted
        """
        self._id = user_id
        self._username = username
        self._password = password
        self._role = role

    # --- Encapsulation: Properties & Accessors ---

    @property
    def id(self) -> Optional[int]:
        """Get the user ID."""
        return self._id

    @id.setter
    def id(self, value: int) -> None:
        """Set the user ID after persistence."""
        self._id = value

    @property
    def username(self) -> str:
        """Get the username."""
        return self._username

    @property
    def password(self) -> str:
        """
        Get the password.
        NOTE (R19 Shortcut): Password is stored and retrieved in plain text without hashing.
        """
        return self._password

    @property
    def role(self) -> str:
        """Get the user's role designation."""
        return self._role

    def is_admin(self) -> bool:
        """
        Polymorphic check whether this user has administrator privileges.
        
        :return: False by default on base User class.
        """
        return False

    def is_employee(self) -> bool:
        """
        Check whether this user has employee role.
        """
        return False

    def can_view_all_incidents(self) -> bool:
        """
        Check whether this user can view incidents reported by any user.
        """
        return True

    def can_delete_incidents(self) -> bool:
        """
        Permission check for deleting incidents.
        
        :return: False for default base users.
        """
        return False

    def to_dict(self) -> dict:
        """
        Convert domain user instance into dictionary representation.
        
        :return: Dictionary containing user attributes
        """
        return {
            "id": self._id,
            "username": self._username,
            "role": self._role
        }


class Analyst(User):
    """
    Represents a SOC Security Analyst.
    Inherits from User with analyst-specific defaults and operational capabilities.
    """

    def __init__(self, username: str, password: str, user_id: Optional[int] = None):
        """
        Initialize an Analyst user entity.
        
        :param username: Analyst username
        :param password: Plaintext password
        :param user_id: Database identifier
        """
        super().__init__(username=username, password=password, role="analyst", user_id=user_id)

    def is_admin(self) -> bool:
        """Analyst is not an administrator."""
        return False

    def can_delete_incidents(self) -> bool:
        """Analysts cannot delete incidents, only view and create."""
        return False


class Admin(User):
    """
    Represents a System Administrator / SOC Lead.
    Inherits from User with full administrative privileges.
    """

    def __init__(self, username: str, password: str, user_id: Optional[int] = None):
        """
        Initialize an Admin user entity.
        
        :param username: Admin username
        :param password: Plaintext password
        :param user_id: Database identifier
        """
        super().__init__(username=username, password=password, role="admin", user_id=user_id)

    def is_admin(self) -> bool:
        """Admin has full administrator permissions."""
        return True

    def can_delete_incidents(self) -> bool:
        """Admins have permission to delete or purge incident records."""
        return True


class Employee(User):
    """
    Represents an internal Employee.
    Can report incidents and view only their own reported incidents.
    """

    def __init__(self, username: str, password: str, user_id: Optional[int] = None):
        """
        Initialize an Employee user entity.
        
        :param username: Employee username
        :param password: Password
        :param user_id: Database identifier
        """
        super().__init__(username=username, password=password, role="employee", user_id=user_id)

    def is_admin(self) -> bool:
        """Employee is not an administrator."""
        return False

    def is_employee(self) -> bool:
        """Employee role identifier."""
        return True

    def can_view_all_incidents(self) -> bool:
        """Employees can only view their own incidents, not those of others."""
        return False

    def can_delete_incidents(self) -> bool:
        """Employees cannot delete incidents."""
        return False


def user_factory(username: str, password: str, role: str = "analyst", user_id: Optional[int] = None) -> User:
    """
    Factory function to instantiate the proper domain User subclass based on role.
    
    :param username: Account username
    :param password: Password hash or string
    :param role: Role string ('admin', 'analyst', or 'employee')
    :param user_id: Database record ID
    :return: Concrete User instance (Admin, Analyst, or Employee)
    """
    normalized_role = (role or "analyst").lower().strip()
    if normalized_role == "admin":
        return Admin(username=username, password=password, user_id=user_id)
    elif normalized_role == "employee":
        return Employee(username=username, password=password, user_id=user_id)
    return Analyst(username=username, password=password, user_id=user_id)
