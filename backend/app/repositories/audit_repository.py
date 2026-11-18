
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, audit_data: dict):
        audit_log = AuditLog(**audit_data)
        self.db.add(audit_log)
        self.db.flush()
        return audit_log

    def get_by_id(self, audit_id: str):
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.id == audit_id)
            .first()
        )

    def list_by_organization(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 100,
    ):
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.organization_id == organization_id
            )
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
    ):
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        skip: int = 0,
        limit: int = 100,
    ):
        return (
            self.db.query(AuditLog)
            .filter(
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id,
            )
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_action(
        self,
        action: str,
        skip: int = 0,
        limit: int = 100,
    ):
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.action == action)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
