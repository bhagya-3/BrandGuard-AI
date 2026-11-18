from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.models.role import Role
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService, AuthServiceError
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    PasswordChangeRequest,
)

router = APIRouter()


def _auth_response(user: User, workspace_id: str | None = None) -> dict:
    return {
        "access_token": create_access_token(
            user.id,
            {"organization_id": user.organization_id},
        ),
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "organization_id": user.organization_id,
            "workspace_id": workspace_id,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
        },
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = AuthService(db).register(
            payload.organization_name,
            payload.full_name,
            str(payload.email),
            payload.password,
        )
        workspace = Workspace(
            organization_id=user.organization_id,
            name="Main workspace",
            created_by=user.id,
        )
        db.add(workspace)
        role = db.query(Role).filter(Role.name == "Creator").first()
        if not role:
            role = Role(name="Creator", description="Creates and reviews content.")
            db.add(role)
        user.roles.append(role)
        db.commit()
        db.refresh(user)
        db.refresh(workspace)
        return _auth_response(user, workspace.id)
    except AuthServiceError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        result = AuthService(db).login(str(payload.email), payload.password)
    except AuthServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = result["user"]
    workspace = (
        db.query(Workspace)
        .filter(Workspace.organization_id == user.organization_id)
        .order_by(Workspace.created_at.asc())
        .first()
    )
    response = _auth_response(user, workspace.id if workspace else None)
    return response


@router.get("/me")
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    workspace = (
        db.query(Workspace)
        .filter(Workspace.organization_id == user.organization_id)
        .order_by(Workspace.created_at.asc())
        .first()
    )
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "organization_id": user.organization_id,
        "workspace_id": workspace.id if workspace else None,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
    }
@router.post("/change-password")
def change_password(
    payload: PasswordChangeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        AuthService(db).change_password(
            user.id,
            payload.current_password,
            payload.new_password,
        )
        db.commit()

        return {
            "success": True,
            "message": "Password changed successfully.",
        }

    except AuthServiceError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc