

from fastapi import HTTPException, status


ROLE_PERMISSIONS = {
    "creator": {
        "document:create",
        "document:read",
        "document:update",
        "review:create",
        "review:read",
        "comment:create",
    },
    "reviewer": {
        "document:read",
        "review:read",
        "finding:read",
        "comment:create",
        "approval:review",
    },
    "manager": {
        "document:create",
        "document:read",
        "document:update",
        "review:create",
        "review:read",
        "comment:create",
        "approval:review",
        "team:manage",
    },
    "admin": {"*"},
    "global_admin": {"*"},
    "publisher": {
        "document:read",
        "approval:read",
        "publication:create",
        "publication:read",
    },
}


def has_global_admin_access(user) -> bool:
    roles = getattr(user, "roles", [])

    role_names = {
        role if isinstance(role, str)
        else getattr(role, "name", "")
        for role in roles
    }

    return "global_admin" in {
        name.lower() for name in role_names
    }


def has_permission(user, permission: str) -> bool:
    roles = getattr(user, "roles", [])

    role_names = {
        role if isinstance(role, str)
        else getattr(role, "name", "")
        for role in roles
    }

    for role_name in role_names:
        allowed = ROLE_PERMISSIONS.get(role_name.lower(), set())

        if "*" in allowed or permission in allowed:
            return True

    return False


def require_permission(user, permission: str):
    if not has_permission(user, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )

    return user
