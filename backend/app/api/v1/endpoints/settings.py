
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.notification_preference import NotificationPreference
from app.models.user import User

router = APIRouter()


def _get_or_create_preferences(
    db: Session,
    user_id: str,
) -> NotificationPreference:
    preferences = (
        db.query(NotificationPreference)
        .filter(NotificationPreference.user_id == user_id)
        .first()
    )

    if preferences is None:
        preferences = NotificationPreference(user_id=user_id)
        db.add(preferences)
        db.commit()
        db.refresh(preferences)

    return preferences


def _preferences_response(preferences: NotificationPreference) -> dict:
    return {
        "in_app_enabled": preferences.in_app_enabled,
        "email_enabled": preferences.email_enabled,
        "security_alerts_enabled": preferences.security_alerts_enabled,
        "document_updates_enabled": preferences.document_updates_enabled,
    }


@router.get("/notifications")
def get_notification_preferences(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    preferences = _get_or_create_preferences(db, user.id)
    return _preferences_response(preferences)


@router.put("/notifications")
def update_notification_preferences(
    payload: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed_fields = {
        "in_app_enabled",
        "email_enabled",
        "security_alerts_enabled",
        "document_updates_enabled",
    }

    if not payload or set(payload.keys()) - allowed_fields:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=422,
            detail="Provide valid notification preference fields.",
        )

    if any(type(value) is not bool for value in payload.values()):
        from fastapi import HTTPException

        raise HTTPException(
            status_code=422,
            detail="Notification preferences must be true or false.",
        )

    preferences = _get_or_create_preferences(db, user.id)

    for field, value in payload.items():
        setattr(preferences, field, value)

    db.commit()
    db.refresh(preferences)

    return {
        "success": True,
        "message": "Notification preferences saved.",
        "preferences": _preferences_response(preferences),
    }
