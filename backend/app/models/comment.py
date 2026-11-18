
import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    document_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("documents.id"), nullable=True
    )
    review_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("reviews.id"), nullable=True
    )
    finding_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("findings.id"), nullable=True
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=False
    )
    parent_comment_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("comments.id"), nullable=True
    )

    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    document = relationship("Document")
    review = relationship("Review")
    finding = relationship("Finding")
    author = relationship("User")
    replies = relationship(
        "Comment",
        back_populates="parent",
        cascade="all, delete-orphan",
    )
    parent = relationship(
        "Comment",
        back_populates="replies",
        remote_side="Comment.id",
    )
