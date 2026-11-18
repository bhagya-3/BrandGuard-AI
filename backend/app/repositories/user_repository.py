from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str):
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str):
        return (
            self.db.query(User)
            .filter(User.email == email.lower().strip())
            .first()
        )

    def get_by_organization(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 50,
    ):
        return (
            self.db.query(User)
            .filter(User.organization_id == organization_id)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, user_data: dict):
        data = user_data.copy()

        if "email" in data:
            data["email"] = data["email"].lower().strip()

        user = User(**data)
        self.db.add(user)
        self.db.flush()
        return user

    def update(self, user: User, update_data: dict):
        allowed_fields = {
            "full_name",
            "email",
            "password_hash",
            "is_active",
            "is_verified",
        }

        for field, value in update_data.items():
            if field in allowed_fields:
                if field == "email" and value:
                    value = value.lower().strip()

                setattr(user, field, value)

        self.db.flush()
        return user

    def deactivate(self, user: User):
        user.is_active = False
        self.db.flush()
        return user

    def email_exists(self, email: str) -> bool:
        return (
            self.db.query(User.id)
            .filter(User.email == email.lower().strip())
            .first()
            is not None
        )
