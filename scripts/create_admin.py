"""Create an administrator for an existing or new organization.

Passwords are requested interactively unless --password-env names an environment
variable containing the password. Never pass a password directly as a CLI value.
"""

import argparse
import getpass
import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy.exc import SQLAlchemyError

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import Organization, Role, User, Workspace
from app.utils.identifiers import normalize_identifier


def parse_args():
    parser = argparse.ArgumentParser(description="Create a BrandGuard organization administrator.")
    parser.add_argument("--email", required=True, help="Administrator email address.")
    parser.add_argument("--name", required=True, help="Administrator's full name.")
    organization = parser.add_mutually_exclusive_group(required=True)
    organization.add_argument("--organization", help="Organization name; created if it does not exist.")
    organization.add_argument("--organization-id", help="ID of an existing organization.")
    parser.add_argument(
        "--password-env",
        help="Environment variable containing the password; otherwise prompt securely.",
    )
    return parser.parse_args()


def read_password(environment_name):
    if environment_name:
        password = os.environ.get(environment_name)
        if not password:
            raise ValueError(f"Environment variable {environment_name} is empty or not set.")
    else:
        password = getpass.getpass("Administrator password (12+ characters): ")
        confirmation = getpass.getpass("Confirm password: ")
        if password != confirmation:
            raise ValueError("Passwords do not match.")

    if len(password) < 12:
        raise ValueError("Password must contain at least 12 characters.")
    return password


def unique_slug(session, name):
    base_slug = normalize_identifier(name)
    slug = base_slug
    suffix = 2
    while session.query(Organization.id).filter_by(slug=slug).first():
        slug = f"{base_slug}-{suffix}"
        suffix += 1
    return slug


def create_admin(email, full_name, organization_name, organization_id, password):
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        normalized_email = email.strip().lower()
        if session.query(User.id).filter_by(email=normalized_email).first():
            raise ValueError("An account with that email already exists; no changes were made.")

        admin_role = session.query(Role).filter(Role.name.ilike("admin")).one_or_none()
        if admin_role is None:
            raise ValueError("The Admin role is missing. Run seed_roles.py first.")

        if organization_id:
            organization = session.query(Organization).filter_by(id=organization_id).one_or_none()
            if organization is None:
                raise ValueError("The requested organization does not exist.")
        else:
            name = organization_name.strip()
            slug = normalize_identifier(name)
            organization = session.query(Organization).filter_by(slug=slug).one_or_none()
            if organization is None:
                organization = Organization(name=name, slug=unique_slug(session, name))
                session.add(organization)
                session.flush()

        user = User(
            organization_id=organization.id,
            email=normalized_email,
            full_name=full_name.strip(),
            password_hash=hash_password(password),
            is_active=True,
            is_verified=True,
        )
        user.roles.append(admin_role)
        session.add(user)
        session.flush()

        has_workspace = session.query(Workspace.id).filter_by(
            organization_id=organization.id
        ).first()
        if not has_workspace:
            session.add(Workspace(
                organization_id=organization.id,
                name="Main workspace",
                created_by=user.id,
            ))

        session.commit()
        return organization.name
    except (SQLAlchemyError, ValueError):
        session.rollback()
        raise
    finally:
        session.close()


def main():
    args = parse_args()
    try:
        password = read_password(args.password_env)
        organization_name = create_admin(
            email=args.email,
            full_name=args.name,
            organization_name=args.organization,
            organization_id=args.organization_id,
            password=password,
        )
    except (SQLAlchemyError, ValueError) as error:
        print(f"Could not create administrator: {error}", file=sys.stderr)
        return 1
    print(f"Administrator {args.email.strip().lower()} created for {organization_name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())