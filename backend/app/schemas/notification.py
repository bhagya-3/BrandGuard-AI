
from datetime import datetime

from app.schemas.common import SchemaBase


class NotificationCreate(SchemaBase):
    user_id: str
    title: str
    message: str
    notification_type: str
    link: str | None = None


class NotificationUpdate(SchemaBase):
    is_read: bool


class NotificationResponse(SchemaBase):
    id: str
    user_id: str
    title: str
    message: str
    notification_type: str
    link: str | None = None
    is_read: bool
    created_at: datetime
