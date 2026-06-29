from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from color_utils import color_distance
import models
import schemas

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[schemas.ProductResponse])
def get_products(
    color: str = None,
    gender: str = None,
    category: str = None,
    subcategory: str = None,
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
    products = query.all()
    if color:
        products = sorted(products, key=lambda p: color_distance(color, p.hex))
    return products
