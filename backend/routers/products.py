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
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    products = db.query(models.Product).all()
    if color:
        products = sorted(products, key=lambda p: color_distance(color, p.hex))
    return products
