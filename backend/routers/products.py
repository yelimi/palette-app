from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from color_utils import color_distance
import models
import schemas

router = APIRouter(prefix="/products", tags=["products"])

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


@router.get("", response_model=schemas.ProductListResponse)
def get_products(
    color: str = None,
    gender: str = None,
    category: str = None,
    subcategory: str = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    query = db.query(models.Product)
    if gender:
        query = query.filter(models.Product.gender == gender)
    if category:
        query = query.filter(models.Product.category == category)
    if subcategory:
        query = query.filter(models.Product.subcategory == subcategory)

    total = query.count()
    products = query.all()

    # 색상 거리 정렬은 DB 레벨에서 불가 → 메모리 정렬 후 페이지 슬라이싱
    if color:
        products = sorted(products, key=lambda p: color_distance(color, p.hex))

    offset = (page - 1) * limit
    page_items = products[offset: offset + limit]

    return schemas.ProductListResponse(
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit,
        items=page_items,
    )
