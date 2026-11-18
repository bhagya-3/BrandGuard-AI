from fastapi import APIRouter

from app.api.v1.endpoints import (
    admin,
    analytics,
    approvals,
    audit,
    auth,
    comments,
    documents,
    findings,
    notifications,
    organizations,
    publishing,
    reviews,
    settings,
    sources,
    users,
    workspaces,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["Organizations"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(findings.router, prefix="/findings", tags=["Findings"])
api_router.include_router(sources.router, prefix="/sources", tags=["Approved Sources"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["Approvals"])
api_router.include_router(comments.router, prefix="/comments", tags=["Comments"])
api_router.include_router(publishing.router, prefix="/publishing", tags=["Publishing"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit Logs"])
api_router.include_router(admin.router, prefix="/admin", tags=["Administration"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
