
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class BrandRule(Base):
    __tablename__ = "brand_rules"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    organization_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    source_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("sources.id"),
        nullable=True,
    )

    brand_value_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("brand_values.id"),
        nullable=True,
    )

    created_by: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    rule_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    match_type: Mapped[str] = mapped_column(
        String(50),
        default="exact",
        nullable=False,
    )

    rule_config: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    severity: Mapped[str] = mapped_column(
        String(30),
        default="medium",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    organization = relationship("Organization")
    source = relationship("Source")
    brand_value = relationship("BrandValue")
    creator = relationship("User")
