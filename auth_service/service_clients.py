"""
HTTP clients for communicating with other microservices from auth service.
"""

import httpx
import os
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class ServiceConfig:
    """Configuration for microservice endpoints."""

    def __init__(self):
        # Service URLs from environment variables or defaults for local development
        self.eli5_service_url = os.getenv("ELI5_SERVICE_URL", "http://localhost:8000")
        self.history_service_url = os.getenv(
            "HISTORY_SERVICE_URL", "http://localhost:8002"
        )

        # HTTP client timeout settings
        self.timeout = float(os.getenv("HTTP_TIMEOUT", "30.0"))
        self.max_retries = int(os.getenv("HTTP_MAX_RETRIES", "3"))


config = ServiceConfig()


class BaseServiceClient:
    """Base class for all service clients with common HTTP functionality."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            timeout=config.timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Make HTTP request with error handling and retries."""
        url = f"{self.base_url}{endpoint}"
        request_headers = headers or {}

        for attempt in range(config.max_retries):
            try:
                logger.info(f"Making {method} request to {url} (attempt {attempt + 1})")

                response = await self.client.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    json=json_data,
                    data=data,
                )

                logger.info(f"Response status: {response.status_code} for {url}")

                if response.status_code < 500:
                    return response

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
                if attempt == config.max_retries - 1:
                    raise HTTPException(
                        status_code=503, detail=f"Service unavailable: {self.base_url}"
                    )
            except Exception as e:
                logger.error(f"Unexpected error in request: {str(e)}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Internal error communicating with service: {str(e)}",
                )

        raise HTTPException(status_code=503, detail="Service communication failed")

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class HistoryServiceClient(BaseServiceClient):
    """Client for communicating with the History Service."""

    def __init__(self):
        super().__init__(config.history_service_url)

    async def notify_user_created(
        self, user_id: int, user_data: Dict[str, Any]
    ) -> bool:
        """Notify history service that a new user was created."""
        try:
            notification_data = {
                "user_id": user_id,
                "event": "user_created",
                "data": user_data,
            }

            response = await self._make_request(
                "POST", "/history/user-events", json_data=notification_data
            )

            return response.status_code == 200

        except Exception as e:
            logger.error(f"Error notifying history service of user creation: {str(e)}")
            return False


# Global client instance
history_client = HistoryServiceClient()


async def cleanup_clients():
    """Cleanup function to close all HTTP clients."""
    await history_client.close()
