import httpx
from typing import Any, Optional

from config import BotConfig


class LMSClient:
    """HTTP client for the LMS backend.
    
    Handles all communication with localhost:42002, including error formatting
    so handlers don't deal with raw tracebacks.
    """

    def __init__(self, config: BotConfig):
        self.base_url = config.LMS_API_BASE_URL
        self.api_key = config.LMS_API_KEY
        self.last_error = ""
        if not self.base_url or not self.api_key:
            raise ValueError("LMS_API_BASE_URL and LMS_API_KEY must be set in .env.bot.secret")

    def _headers(self) -> dict[str, str]:
        """Return standard headers with Bearer auth."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _format_error(self, error: Exception) -> str:
        """Convert raw exceptions into user-friendly messages."""
        error_str = str(error)

        # Connection errors (connection refused, timeout, etc.)
        if "connection" in error_str.lower() or "refused" in error_str.lower():
            msg = f"Backend error: connection refused ({self.base_url}). Check that the services are running."
        elif "timeout" in error_str.lower():
            msg = f"Backend error: timeout connecting to {self.base_url}. The service may be overloaded."
        # HTTP errors (4xx, 5xx)
        elif "502" in error_str or "Bad Gateway" in error_str:
            msg = "Backend error: HTTP 502 Bad Gateway. The backend service may be down."
        elif "503" in error_str or "Service Unavailable" in error_str:
            msg = "Backend error: HTTP 503 Service Unavailable. The backend is temporarily unavailable."
        elif "404" in error_str or "Not Found" in error_str:
            msg = "Backend error: HTTP 404 Not Found. The endpoint may have changed."
        else:
            # Generic fallback
            msg = f"Backend error: {error_str[:100]}"

        self.last_error = msg
        return msg

    def get_last_error(self) -> str:
        """Return the last error message."""
        return self.last_error

    def get_items(self) -> Optional[list[dict[str, Any]]]:
        """Fetch all items (labs and tasks).
        
        Returns:
            List of items, or None if an error occurs.
        """
        try:
            with httpx.Client(trust_env=False) as client:
                response = client.get(
                    f"{self.base_url}/items/",
                    headers=self._headers(),
                    timeout=5.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self._format_error(e)
            return None

    def get_pass_rates(self, lab_id: str) -> Optional[list[dict[str, Any]]]:
        """Fetch per-task pass rates for a lab.
        
        Args:
            lab_id: The lab identifier (e.g., "lab-04").
        
        Returns:
            Pass rate data, or None if an error occurs.
        """
        try:
            with httpx.Client(trust_env=False) as client:
                response = client.get(
                    f"{self.base_url}/analytics/pass-rates",
                    params={"lab": lab_id},
                    headers=self._headers(),
                    timeout=5.0,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            self._format_error(e)
            return None
