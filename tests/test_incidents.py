"""
Tests for Sentinel Incident Management and Features (R2 - R8).
Verifies incident creation, search filtering, comments (raw HTML), attachments,
external URL link previews, and cookie-based preference filtering.
"""

import os
import io
import tempfile
import unittest
from unittest.mock import patch
from app import create_app


class IncidentTestCase(unittest.TestCase):
    """
    Test suite validating core incident workflows and features.
    """

    def setUp(self):
        """Configure test application environment and authenticated test session."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.upload_dir = tempfile.mkdtemp()

        self.app = create_app({
            "TESTING": True,
            "DATABASE_PATH": self.db_path,
            "UPLOAD_FOLDER": self.upload_dir,
            "SECRET_KEY": "test-key"
        })
        self.client = self.app.test_client()

        # Register and establish an active test session
        self.app.auth_service.register("lead_analyst", "analystpass", role="analyst")
        with self.client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "lead_analyst"
            sess["role"] = "analyst"

    def tearDown(self):
        """Clean up temporary resources."""
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_create_and_view_incident(self):
        """Verify incident creation and retrieval on detail page (R2, R3)."""
        response = self.client.post("/incidents/new", data={
            "title": "DDoS Attack against DMZ Gateway",
            "description": "High volume SYN flood detected on edge router ingress interface.",
            "severity": "HIGH",
            "source_url": ""
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"DDoS Attack against DMZ Gateway", response.data)
        self.assertIn(b"HIGH", response.data)
        self.assertIn(b"SYN flood detected", response.data)

    def test_search_incident_by_substring(self):
        """Verify incident search filtering by substring match (R5 / Feature 2)."""
        service = self.app.incident_service
        service.create_incident("Phishing Campaign Wave 1", "Targeted executive team", "MEDIUM", "lead_analyst")
        service.create_incident("Ransomware Outbreak on Host-12", "Encrypted files found in accounting", "CRITICAL", "lead_analyst")
        service.create_incident("Port Scan Activity", "External reconnaissance observed", "LOW", "lead_analyst")

        # Search for 'Ransomware'
        res1 = self.client.get("/incidents?q=Ransomware")
        self.assertEqual(res1.status_code, 200)
        self.assertIn(b"Ransomware Outbreak", res1.data)
        self.assertNotIn(b"Phishing Campaign", res1.data)
        self.assertNotIn(b"Port Scan Activity", res1.data)

        # Search for substring in description: 'accounting'
        res2 = self.client.get("/incidents?q=accounting")
        self.assertEqual(res2.status_code, 200)
        self.assertIn(b"Ransomware Outbreak", res2.data)

    def test_comments_rendered_raw_html(self):
        """Verify users can post comments and comments render raw HTML without escaping (R4 / Feature 1)."""
        service = self.app.incident_service
        incident = service.create_incident("SQL Injection Test Record", "Testing notes", "LOW", "lead_analyst")

        # Post comment containing raw HTML tags
        raw_html_payload = "<strong>Forensic Note:</strong> Host isolated successfully! <em>Check firewall.</em>"
        comment_res = self.client.post(f"/incidents/{incident.id}/comments", data={
            "content": raw_html_payload
        }, follow_redirects=True)

        self.assertEqual(comment_res.status_code, 200)
        # Verify the raw HTML tag is directly in response body unescaped
        self.assertIn(b"<strong>Forensic Note:</strong>", comment_res.data)
        self.assertIn(b"<em>Check firewall.</em>", comment_res.data)

    def test_source_link_preview(self):
        """Verify external URL title extraction (R7 / Feature 4)."""
        # Mock urllib request to simulate external webpage title extraction
        mock_html = b"<html><head><title>Threat Advisory CVE-2026-9999</title></head><body>Alert details</body></html>"
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_resp = mock_urlopen.return_value.__enter__.return_value
            mock_resp.read.return_value = mock_html

            res = self.client.post("/incidents/new", data={
                "title": "Zero-Day Vulnerability Advisory",
                "description": "Critical flaw detected in edge appliance.",
                "severity": "CRITICAL",
                "source_url": "https://example-cert.org/advisory/2026-9999"
            }, follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Threat Advisory CVE-2026-9999", res.data)

    def test_file_upload_attachment(self):
        """Verify file attachment upload and direct retrieval (R6 / Feature 3)."""
        test_file_content = b"[SYSTEM LOG] Alert: Unauthorized access at 14:22:00"
        test_file = (io.BytesIO(test_file_content), "firewall_dump.log")

        res = self.client.post("/incidents/new", data={
            "title": "Firewall Breached",
            "description": "Log dump attached for review.",
            "severity": "HIGH",
            "source_url": "",
            "attachment": test_file
        }, content_type="multipart/form-data", follow_redirects=True)

        self.assertEqual(res.status_code, 200)
        self.assertIn(b"firewall_dump.log", res.data)

        # Download the file
        download_res = self.client.get("/uploads/firewall_dump.log")
        self.assertEqual(download_res.status_code, 200)
        self.assertEqual(download_res.data, test_file_content)
        download_res.close()

    def test_preferences_cookie(self):
        """Verify default list filter stored in cookie and applied to incident list (R8 / Feature 5)."""
        service = self.app.incident_service
        service.create_incident("Low event", "Just info", "LOW", "lead_analyst")
        service.create_incident("Critical alert", "Emergency", "CRITICAL", "lead_analyst")

        # Save cookie preference for CRITICAL
        pref_res = self.client.post("/preferences", data={
            "default_severity": "CRITICAL"
        })
        self.assertEqual(pref_res.status_code, 302)

        # Set cookie on test client
        self.client.set_cookie("sentinel_severity_pref", "CRITICAL")

        # Navigate to incident list without query params
        list_res = self.client.get("/incidents")
        self.assertEqual(list_res.status_code, 200)
        self.assertIn(b"Critical alert", list_res.data)
        self.assertNotIn(b"Low event", list_res.data)


if __name__ == "__main__":
    unittest.main()
