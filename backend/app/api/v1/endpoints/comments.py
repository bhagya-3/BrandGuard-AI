from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.models.comment import Comment
from app.models.review import Review
from app.models.user import User
from app.services.audit_service import AuditService


router = APIRouter()


class CommentCreate(BaseModel):
    review_id: str
    finding_id: str | None = None
    body: str = Field(min_length=1, max_length=5000)


def _comment_response(comment: Comment) -> dict:
    return {
        "id": comment.id,
        "review_id": comment.review_id,
        "finding_id": comment.finding_id,
        "body": comment.body,
        "author": comment.author.full_name,
        "created_at": comment.created_at,
    }


@router.get("/")
def list_comments(
    review_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.organization_id == user.organization_id,
    ).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")
    comments = (
        db.query(Comment)
        .filter(Comment.review_id == review_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return [_comment_response(comment) for comment in comments]


@router.post("/", status_code=201)
def create_comment(
    payload: CommentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review = db.query(Review).filter(
        Review.id == payload.review_id,
        Review.organization_id == user.organization_id,
    ).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")

    comment = Comment(
        document_id=review.document_id,
        review_id=review.id,
        finding_id=payload.finding_id,
        user_id=user.id,
        body=payload.body.strip(),
    )
    db.add(comment)
    AuditService(db).record_event(
        action="comment.created",
        entity_type="review",
        entity_id=review.id,
        user_id=user.id,
        organization_id=user.organization_id,
        details={"comment_id": comment.id, "finding_id": payload.finding_id},
    )
    db.commit()
    db.refresh(comment)
    return _comment_response(comment)