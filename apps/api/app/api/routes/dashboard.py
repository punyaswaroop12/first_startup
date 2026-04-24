from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.schemas.dashboard import DashboardOverviewResponse
from app.services.dashboard import build_dashboard_overview

router = APIRouter()


@router.get("/overview", response_model=DashboardOverviewResponse)
def overview(db: Session = Depends(get_db), current_user=Depends(get_current_user)) -> DashboardOverviewResponse:
    return build_dashboard_overview(db=db, current_user=current_user)

