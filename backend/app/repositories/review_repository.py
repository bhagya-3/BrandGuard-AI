
from sqlalchemy.orm import Session

from app.models.review import Review


class ReviewRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, review_id: str):
        return (
            self.db.query(Review)
            .filter(Review.id == review_id)
            .first()
        )

    def get_by_id_and_org(
        self,
        review_id: str,
        organization_id: str,
    ):
        return (
            self.db.query(Review)
            .filter(
                Review.id == review_id,
                Review.organization_id == organization_id,
            )
            .first()
        )

    def list_by_organization(
        self,
        organization_id: str,
        skip: int = 0,
        limit: int = 50,
    ):
        return (
            self.db.query(Review)
            .filter(Review.organization_id == organization_id)
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def list_by_document(
        self,
        document_id: str,
        skip: int = 0,
        limit: int = 50,
    ):
        return (
            self.db.query(Review)
            .filter(Review.document_id == document_id)
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, review_data: dict):
        review = Review(**review_data)
        self.db.add(review)
        self.db.flush()
        return review

    def update(self, review: Review, update_data: dict):
        allowed_fields = {
            "status",
            "overall_score",
            "summary",
            "started_at",
            "completed_at",
        }

        for field, value in update_data.items():
            if field in allowed_fields:
                setattr(review, field, value)

        self.db.flush()
        return review

    def update_status(self, review: Review, status: str):
        review.status = status
        self.db.flush()
        return review

    def delete(self, review: Review):
        self.db.delete(review)
        self.db.flush()

