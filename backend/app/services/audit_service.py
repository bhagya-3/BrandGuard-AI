
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.audit_repository import AuditRepository


class AuditService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = AuditRepository(db)

    def record_event(
        self,
        action: str,
        entity_type: str,
        entity_id: str | None = None,
        user_id: str | None = None,
        organization_id: str | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:

        audit_data = {
            "organization_id": organization_id,
            "user_id": user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details or {},
            "ip_address": ip_address,
        }

        return self.repository.create(audit_data)

    def get_organization_logs(
        self,
        organization_id: str,
        limit: int = 100,
    ):
        if limit < 1 or limit > 500:
            raise ValueError(
                "Limit must be between 1 and 500."
            )

        return self.repository.list_by_organization(
            organization_id,
            limit=limit,
        )

    def get_user_logs(
        self,
        user_id: str,
        limit: int = 100,
    ):
        if limit < 1 or limit > 500:
            raise ValueError(
                "Limit must be between 1 and 500."
            )

        return self.repository.list_by_user(
            user_id,
            limit=limit,
        )

    def get_entity_logs(
        self,
        entity_type: str,
        entity_id: str,
    ):
        return self.repository.list_by_entity(
            entity_type,
            entity_id,
        )
