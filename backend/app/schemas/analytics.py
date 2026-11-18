
from datetime import datetime

from app.schemas.common import SchemaBase


class OverviewAnalytics(SchemaBase):
    total_documents: int = 0
    total_reviews: int = 0
    total_findings: int = 0
    pending_approvals: int = 0
    published_documents: int = 0
    active_users: int = 0


class SeverityAnalytics(SchemaBase):
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0


class ReviewTrendItem(SchemaBase):
    date: datetime
    total_reviews: int
    completed_reviews: int
    failed_reviews: int


class CategoryAnalytics(SchemaBase):
    category: str
    count: int


class DashboardAnalytics(SchemaBase):
    overview: OverviewAnalytics
    severity: SeverityAnalytics
    review_trends: list[ReviewTrendItem] = []
    findings_by_category: list[CategoryAnalytics] = []
