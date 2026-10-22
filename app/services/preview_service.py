"""
External link preview service for threat intelligence and source references.
Fetches external webpage contents and extracts the HTML <title> tag.
"""

import re
import urllib.request
from typing import Optional


class PreviewService:
    """
    Service responsible for fetching remote web pages and extracting title metadata.
    NOTE (R19 Shortcut): Does NOT perform URL validation, IP address allow/deny listing,
    or internal subnet blocking (e.g. 127.0.0.1, 169.254.169.254, RFC1918 addresses).
    This intentionally introduces Server-Side Request Forgery (SSRF) exposure.
    """

    def __init__(self, timeout: int = 5):
        """
        Initialize PreviewService.
        
        :param timeout: Request timeout in seconds
        """
        self._timeout = timeout

    def fetch_source_title(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from external URL and extract the page title using regex.
        
        NOTE (R19 Shortcut): Unvalidated remote URL retrieval.
        
        :param url: User-supplied URL string
        :return: Extracted title string or fallback message
        """
        if not url or not url.strip():
            return None

        clean_url = url.strip()
        # Automatically prepend http scheme if missing
        if not (clean_url.startswith("http://") or clean_url.startswith("https://")):
            clean_url = "http://" + clean_url

        try:
            req = urllib.request.Request(
                clean_url,
                headers={"User-Agent": "Sentinel-SOC-Bot/1.0 (Nexus Digital Solutions)"}
            )
            with urllib.request.urlopen(req, timeout=self._timeout) as response:
                content = response.read(65536).decode("utf-8", errors="ignore")
                
                # Extract <title> content using regex
                match = re.search(r"<title[^>]*>(.*?)</title>", content, re.IGNORECASE | re.DOTALL)
                if match:
                    title_text = match.group(1).strip()
                    # Collapse multiple whitespaces
                    return " ".join(title_text.split())
                return "No Title Found"
        except Exception as e:
            # Return error as title preview to give immediate visual feedback in prototype
            return f"Preview Unavailable: {str(e)}"
