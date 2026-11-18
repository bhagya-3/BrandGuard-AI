from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.workspace import Workspace


router = APIRouter()


@router.get("/")
def list_workspaces(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    workspaces = (
        db.query(Workspace)
        .filter(Workspace.organization_id == user.organization_id)
        .order_by(Workspace.created_at.asc())
        .all()
    )
    return [
        {"id": workspace.id, "name": workspace.name, "description": workspace.description}
        for workspace in workspaces
    ]