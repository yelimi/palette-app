from fastapi import APIRouter, Depends, Query
from auth import get_current_user
from color_utils import recommend_colors
import schemas
import models

router = APIRouter(prefix="/colors", tags=["colors"])


@router.get("/recommend", response_model=list[schemas.ColorRecommendation])
def get_color_recommendations(
    color: str = Query(..., description="기준 색상 hex (예: #D4B896)"),
    top_n: int = Query(default=5, ge=1, le=10),
    _: models.User = Depends(get_current_user),
):
    return recommend_colors(color, top_n=top_n)
