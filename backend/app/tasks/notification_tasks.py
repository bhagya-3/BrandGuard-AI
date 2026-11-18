
import asyncio
import logging

from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.notification import Notification
from app.models.user import User
from app.integrations.email.email_service import send_email
from app.integrations.slack.slack_service import send_slack_notification

logger = logging.getLogger(__name__)


@celery_app.task(
    name="brandguard.notifications.send_notification",
    max_retries=3,
    default_retry_delay=30,
)
def send_notification_task(
    user_id: str,
    title: str,
    message: str,
    notification_type: str = "general",
    link: str = None,
    send_email_alert: bool = False,
    send_slack_alert: bool = False,
):
    """
    Create an in-app notification and optionally send email/Slack alerts.
    """
    db = SessionLocal()

    try:
        user = db.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()

        if user is None:
            return {
                "success": False,
                "message": "User not found.",
            }

        notification = Notification(
            user_id=user.id,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
            is_read=False,
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        email_sent = False
        slack_sent = False

        if send_email_alert and user.email:
            try:
                email_sent = bool(
                    send_email(
                        recipient=user.email,
                        subject=title,
                        body=message,
                    )
                )
            except Exception:
                logger.exception("Email notification failed for user %s.", user_id)

        if send_slack_alert:
            try:
                slack_sent = bool(
                    asyncio.run(
                        send_slack_notification(
                            message=message,
                            title=title,
                        )
                    )
                )
            except Exception:
                logger.exception("Slack notification failed.")

        return {
            "success": True,
            "notification_id": str(notification.id),
            "email_sent": email_sent,
            "slack_sent": slack_sent,
        }

    except Exception:
        db.rollback()
        logger.exception(
            "Unable to create notification for user %s.",
            user_id,
        )
        raise

    finally:
        db.close()
