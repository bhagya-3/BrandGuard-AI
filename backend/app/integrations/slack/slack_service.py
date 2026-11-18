
import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def send_slack_notification(
    message: str,
    title: str = "BrandGuard AI Notification",
) -> bool:
    """Send a notification using a Slack Incoming Webhook."""

    webhook_url = settings.SLACK_WEBHOOK_URL

    if not webhook_url:
        logger.warning("Slack integration is not configured.")
        return False

    payload = {
        "text": f"*{title}*\n{message}"
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                webhook_url,
                json=payload,
            )
            response.raise_for_status()

        logger.info("Slack notification sent.")
        return True

    except httpx.HTTPError:
        logger.exception("Failed to send Slack notification.")
        return False
