
import httpx

from urllib.parse import urlencode

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

MICROSOFT_BASE_URL = "https://login.microsoftonline.com"


def get_entra_authorization_url(state: str) -> str:
    """Generate Microsoft Entra authorization URL."""

    if not settings.ENTRA_TENANT_ID:
        raise RuntimeError("Microsoft Entra tenant is not configured.")

    endpoint = (
        f"{MICROSOFT_BASE_URL}/"
        f"{settings.ENTRA_TENANT_ID}/oauth2/v2.0/authorize"
    )

    params = {
        "client_id": settings.ENTRA_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.ENTRA_REDIRECT_URI,
        "response_mode": "query",
        "scope": "openid profile email User.Read",
        "state": state,
    }

    return f"{endpoint}?{urlencode(params)}"


async def exchange_entra_code(code: str) -> dict:
    """Exchange Microsoft authorization code for tokens."""

    if not settings.ENTRA_CLIENT_ID or not settings.ENTRA_CLIENT_SECRET:
        raise RuntimeError("Microsoft Entra OAuth is not configured.")

    endpoint = (
        f"{MICROSOFT_BASE_URL}/"
        f"{settings.ENTRA_TENANT_ID}/oauth2/v2.0/token"
    )

    payload = {
        "client_id": settings.ENTRA_CLIENT_ID,
        "client_secret": settings.ENTRA_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.ENTRA_REDIRECT_URI,
        "grant_type": "authorization_code",
        "scope": "openid profile email User.Read",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            endpoint,
            data=payload,
        )
        response.raise_for_status()
        return response.json()


async def get_entra_user_profile(access_token: str) -> dict:
    """Retrieve the signed-in Microsoft user's profile."""

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            "https://graph.microsoft.com/v1.0/me",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()
