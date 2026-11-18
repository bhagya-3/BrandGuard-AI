"""Idempotently seed built-in roles and permissions.

Run from the backend directory so the configured DATABASE_URL is loaded:
    python ..\\scripts\\seed_roles.py
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy.exc import SQLAlchemyError

from app.core.database import Base, SessionLocal, engine
from app.core.permissions import ROLE_PERMISSIONS
from app import models


ROLE_DESCRIPTIONS = {
    "creator": "Creates and reviews content.",
    "reviewer": "Reviews content and provides findings.",
    "manager": "Manages team workflows and approvals.",
    "admin": "Manages all organization workspace functions.",
    "publisher": "Publishes content that has completed approval.",
}


def seed_roles() -> tuple[int, int]:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        permission_names = sorted({
            permission
            for permissions in ROLE_PERMISSIONS.values()
            for permission in permissions
        })
        permission_models = {}
        for name in permission_names:
            permission = session.query(models.Permission).filter_by(name=name).one_or_none()
            if permission is None:
                permission = models.Permission(
                    name=name,
                    description=(
                        "All permissions for organization administrators."
                        if name == "*"
                        else f"Allows the {name} operation."
                    ),
                )
                session.add(permission)
            permission_models[name] = permission

        created_roles = 0
        for name, permissions in ROLE_PERMISSIONS.items():
            role = session.query(models.Role).filter_by(name=name.title()).one_or_none()
            if role is None:
                role = models.Role(
                    name=name.title(),
                    description=ROLE_DESCRIPTIONS[name],
                )
                session.add(role)
                created_roles += 1
            else:
                role.description = ROLE_DESCRIPTIONS[name]
            role.permissions = [permission_models[item] for item in sorted(permissions)]

        session.commit()
        return created_roles, len(permission_names)
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


def main() -> int:
    try:
        created_roles, permission_count = seed_roles()
    except SQLAlchemyError as error:
        print(f"Could not seed roles: {error}", file=sys.stderr)
        return 1
    print(f"Role seed complete: {created_roles} role(s) created; {permission_count} permission(s) checked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())