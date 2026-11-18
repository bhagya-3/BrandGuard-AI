
from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationServiceError(Exception):
    pass


class NotificationService:

    def __init__(self, db: Session):
        self.db = db

    def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: str,
        link: str | None = None,
    ) -> Notification:

        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
            is_read=False,
        )

        self.db.add(notification)
        self.db.flush()

        return notification

    def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
    ):
        query = self.db.query(Notification).filter(
            Notification.user_id == user_id
        )

        if unread_only:
            query = query.filter(
                Notification.is_read.is_(False)
            )

        return query.order_by(
            Notification.created_at.desc()
        ).all()

    def mark_as_read(
        self,
        notification_id: str,
        user_id: str,
    ) -> Notification:

        notification = (
            self.db.query(Notification)
            .filter(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
            .first()
        )

        if not notification:
            raise NotificationServiceError(
                "Notification not found."
            )

        notification.is_read = True
        self.db.flush()

        return notification

    def mark_all_as_read(self, user_id: str) -> int:

        notifications = (
            self.db.query(Notification)
            .filter(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .all()
        )

        for notification in notifications:
            notification.is_read = True

        self.db.flush()

        return len(notifications)
