from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.permissions import require_permission
from app.models.user import User
from app.services.user_service import UserService


router = APIRouter()


@router.get("/")
def list_users(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_permission(user, "team:manage")

    if not user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not assigned to an organization.",
        )

    members = UserService(db).list_users(user.organization_id)

    return [
        {
            "id": member.id,
            "full_name": member.full_name,
            "email": member.email,
            "roles": [role.name for role in member.roles],
            "is_active": member.is_active,
            "is_verified": member.is_verified,
            "created_at": member.created_at,
            "updated_at": member.updated_at,
        }
        for member in members
    ]

@router.get("/{user_id}")
def get_user_details(
    user_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_permission(user, "team:manage")

    if not user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not assigned to an organization.",
        )

    from app.services.user_service import UserServiceError

    try:
        member = UserService(db).get_user(
            user_id,
            user.organization_id,
        )
    except UserServiceError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace member not found.",
        )

    return {
        "id": member.id,
        "full_name": member.full_name,
        "email": member.email,
        "roles": [role.name for role in member.roles],
        "is_active": member.is_active,
        "is_verified": member.is_verified,
        "created_at": member.created_at,
        "updated_at": member.updated_at,
    }
@router.patch("/{user_id}/status")
def update_user_status(
    user_id: str,
    is_active: bool,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    require_permission(user, "team:manage")

    if not user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is not assigned to an organization.",
        )

    if user_id == user.id and not is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account.",
        )

    from app.services.user_service import UserServiceError

    try:
        service = UserService(db)
        member = service.get_user(user_id, user.organization_id)

        if is_active:
            member.is_active = True
            db.flush()
        else:
            service.deactivate_user(user_id, user.organization_id)

        db.commit()
        db.refresh(member)

    except UserServiceError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace member not found.",
        )

    return {
        "id": member.id,
        "full_name": member.full_name,
        "email": member.email,
        "is_active": member.is_active,
    }