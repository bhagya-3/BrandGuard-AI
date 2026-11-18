
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository


class UserServiceError(Exception):
    pass


class UserService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = UserRepository(db)

    def get_user(
        self,
        user_id: str,
        organization_id: str,
    ):
        user = self.repository.get_by_id(user_id)

        if not user or user.organization_id != organization_id:
            raise UserServiceError("User not found.")

        return user

    def list_users(self, organization_id: str):
        return self.repository.get_by_organization(
            organization_id
        )

    def update_user(
        self,
        user_id: str,
        organization_id: str,
        updates: dict,
    ):
        user = self.get_user(user_id, organization_id)

        allowed_fields = {
            "full_name",
            "email",
        }

        for field, value in updates.items():
            if field not in allowed_fields or value is None:
                continue

            if field == "email":
                value = value.strip().lower()

                existing = self.repository.get_by_email(value)

                if existing and existing.id != user.id:
                    raise UserServiceError(
                        "Email is already in use."
                    )

            setattr(user, field, value)

        self.db.flush()
        return user

    def deactivate_user(
        self,
        user_id: str,
        organization_id: str,
    ):
        user = self.get_user(user_id, organization_id)

        if not user.is_active:
            return user

        self.repository.deactivate(user)

        return user
