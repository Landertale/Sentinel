"""
Tests for Sentinel authentication system (R1).
Validates user registration, login with plain-text passwords, duplicate checks, and session management.
"""

import os
import unittest
import tempfile
from app import create_app
from app.models.user import Analyst, Admin


class AuthTestCase(unittest.TestCase):
    """
    Test cases verifying end-to-end authentication flows and OOP domain models.
    """

    def setUp(self):
        """Set up test application context with isolated temporary SQLite database."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.upload_dir = tempfile.mkdtemp()
        
        self.app = create_app({
            "TESTING": True,
            "DATABASE_PATH": self.db_path,
            "UPLOAD_FOLDER": self.upload_dir,
            "SECRET_KEY": "test-key"
        })
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up temporary database and files."""
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_domain_model_hierarchy(self):
        """Verify OOP inheritance and polymorphism between User, Analyst, and Admin."""
        analyst = Analyst(username="analyst_user", password="secret_plain_text")
        admin = Admin(username="admin_user", password="admin_plain_text")

        self.assertFalse(analyst.is_admin())
        self.assertFalse(analyst.can_delete_incidents())
        self.assertEqual(analyst.role, "analyst")

        self.assertTrue(admin.is_admin())
        self.assertTrue(admin.can_delete_incidents())
        self.assertEqual(admin.role, "admin")

    def test_registration_success(self):
        """Verify successful user registration via AuthService and HTTP route."""
        response = self.client.post("/register", data={
            "username": "sarah_connor",
            "password": "terminator_plain_password",
            "role": "analyst"
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registration successful", response.data)

        # Confirm user exists in repository with plain text password
        user = self.app.auth_service.login("sarah_connor", "terminator_plain_password")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "sarah_connor")
        self.assertEqual(user.password, "terminator_plain_password")

    def test_registration_duplicate_username(self):
        """Verify system rejects duplicate username registration."""
        self.app.auth_service.register("duplicate_user", "pass123")
        
        response = self.client.post("/register", data={
            "username": "duplicate_user",
            "password": "new_password",
            "role": "analyst"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Username already exists", response.data)

    def test_login_and_logout_flow(self):
        """Verify user login creates session and logout destroys it."""
        self.app.auth_service.register("soc_analyst", "hunter2", role="analyst")

        # Successful login
        login_res = self.client.post("/login", data={
            "username": "soc_analyst",
            "password": "hunter2"
        }, follow_redirects=True)
        
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b"Incident Management Dashboard", login_res.data)

        with self.client.session_transaction() as sess:
            self.assertEqual(sess.get("username"), "soc_analyst")

        # Logout
        logout_res = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(logout_res.status_code, 200)
        self.assertIn(b"SOC Portal Login", logout_res.data)

        with self.client.session_transaction() as sess:
            self.assertNotIn("user_id", sess)

    def test_login_invalid_credentials(self):
        """Verify rejection of invalid login credentials."""
        self.app.auth_service.register("valid_user", "correct_password")

        res = self.client.post("/login", data={
            "username": "valid_user",
            "password": "wrong_password"
        }, follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Invalid username or password", res.data)


if __name__ == "__main__":
    unittest.main()
