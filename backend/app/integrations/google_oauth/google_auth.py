
import httpx

from urllib.parse import urlencode

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_TOKEN_INFO_URL = "https://oauth2.googleapis.com/tokeninfo"


def get_google_authorization_url(state: str) -> str:
    """Generate Google OAuth authorization URL."""

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }

    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


async def exchange_google_code(code: str) -> dict:
    """Exchange Google authorization code for tokens."""

    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise RuntimeError("Google OAuth is not configured.")

    payload = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            GOOGLE_TOKEN_URL,
            data=payload,
        )
        response.raise_for_status()
        return response.json()


async def verify_google_id_token(id_token: str) -> dict:
    """Validate a Google ID token and return its claims."""

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            GOOGLE_TOKEN_INFO_URL,
            params={"id_token": id_token},
        )
        response.raise_for_status()
        claims = response.json()

    if claims.get("aud") != settings.GOOGLE_CLIENT_ID:
        raise ValueError("Google token audience mismatch.")

    if claims.get("iss") not in (
        "accounts.google.com",
        "https://accounts.google.com",
    ):
        raise ValueError("Invalid Google token issuer.")

    if claims.get("email_verified") != "true":
        raise ValueError("Google email is not verified.")

    return claims
