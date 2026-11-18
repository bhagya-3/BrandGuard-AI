from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.audit_service import AuditService


router = APIRouter()


@router.get("/")
def list_audit_events(
    limit: int = 100,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    limit = min(max(limit, 1), 500)
    entries = AuditService(db).get_organization_logs(
        user.organization_id,
        limit,
    )
    return [
        {
            "id": entry.id,
            "action": entry.action,
            "entity_type": entry.entity_type,
            "entity_id": entry.entity_id,
            "user_id": entry.user_id,
            "details": entry.details,
            "created_at": entry.created_at,
        }
        for entry in entries
    ]