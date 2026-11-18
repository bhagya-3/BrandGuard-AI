
import re

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.organization import Organization
from app.repositories.user_repository import UserRepository
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


class AuthServiceError(Exception):
    pass


class AuthService:

    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def register(
        self,
        organization_name: str,
        full_name: str,
        email: str,
        password: str,
    ) -> User:

        email = email.strip().lower()
        organization_name = organization_name.strip()
        full_name = full_name.strip()

        # Check whether the email is already registered.
        if self.users.email_exists(email):
            raise AuthServiceError("Email is already registered.")

        # Generate a unique organization slug.
        base_slug = self._make_slug(organization_name)
        slug = base_slug
        counter = 2

        while (
            self.db.query(Organization)
            .filter(Organization.slug == slug)
            .first()
        ):
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Create the organization.
        organization = Organization(
            name=organization_name,
            slug=slug,
            is_active=True,
        )

        self.db.add(organization)
        self.db.flush()

        # Create the organization user.
        user = User(
            organization_id=organization.id,
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            is_active=True,
            is_verified=False,
        )

        self.db.add(user)
        self.db.flush()

        return user

    def login(self, email: str, password: str) -> dict:

        user = self.users.get_by_email(email.strip().lower())

        if not user or not verify_password(password, user.password_hash):
            raise AuthServiceError("Invalid email or password.")

        if not user.is_active:
            raise AuthServiceError("This account is inactive.")

        token = create_access_token(
            subject=user.id,
            additional_claims={
                "organization_id": user.organization_id,
            },
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user,
        }

    def change_password(
        self,
        user_id: str,
        current_password: str,
        new_password: str,
    ) -> bool:

        user = self.users.get_by_id(user_id)

        if not user:
            raise AuthServiceError("User not found.")

        if not verify_password(current_password, user.password_hash):
            raise AuthServiceError("Current password is incorrect.")

        user.password_hash = hash_password(new_password)
        self.db.flush()

        return True

    @staticmethod
    def _make_slug(value: str) -> str:

        slug = re.sub(
            r"[^a-z0-9]+",
            "-",
            value.lower().strip(),
        ).strip("-")

        if not slug:
            raise AuthServiceError("Invalid organization name.")

        return slug
