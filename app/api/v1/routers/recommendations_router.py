from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import get_current_user
from app.database import get_db
from app.schemas.recomendations import RecommendationsResponse, RecommendationItem
from app.schemas.user import UserPublic
from app.services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("", response_model=RecommendationsResponse)
async def get_recommendations(
        n: int = Query(5, ge=1, le=50),
        session: AsyncSession = Depends(get_db),
        current_user: UserPublic = Depends(get_current_user),
):
    service = RecommendationService()
    ranked = await service.get_user_recommendations(session, user_id=current_user.id, n_recommendations=n)
    return RecommendationsResponse(items=[RecommendationItem(**r.__dict__) for r in ranked])
