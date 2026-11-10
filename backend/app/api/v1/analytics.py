from fastapi import APIRouter, Depends
from app.api.deps import DB, require_permissions
from app.core.permissions import PermissionCode
from app.schemas.analytics import DashboardStats
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

def get_analytics_service(session: DB) -> AnalyticsService:
    return AnalyticsService(session)

@router.get(
    "/dashboard", 
    response_model=DashboardStats, 
    dependencies=[Depends(require_permissions(PermissionCode.REPORTS_VIEW.value))]
)
async def get_dashboard(svc: AnalyticsService = Depends(get_analytics_service)) -> DashboardStats:
    return await svc.get_dashboard_stats()