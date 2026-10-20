from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
import models
import schemas

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("", response_model=list[schemas.CartItemResponse])
def get_cart(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return db.query(models.Cart).filter(models.Cart.user_id == current_user.id).all()


@router.post("", response_model=schemas.CartItemResponse, status_code=201)
def add_to_cart(
    body: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    product = db.get(models.Product, body.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    item = models.Cart(user_id=current_user.id, product_id=body.product_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{cart_id}", status_code=204)
def delete_cart_item(
    cart_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    item = db.query(models.Cart).filter(
        models.Cart.id == cart_id,
        models.Cart.user_id == current_user.id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="장바구니 항목을 찾을 수 없습니다.")
    db.delete(item)
    db.commit()
