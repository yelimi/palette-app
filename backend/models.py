from datetime import datetime
from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    cart_items: Mapped[list["Cart"]] = relationship("Cart", back_populates="user")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)       # 남성 / 여성 / 공용
    category: Mapped[str] = mapped_column(String(100), nullable=False)    # 상의 / 아우터 / 바지 / 원피스·스커트
    subcategory: Mapped[str] = mapped_column(String(100), nullable=False) # 긴소매 티셔츠 / 카디건 등
    color_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hex: Mapped[str] = mapped_column(String(7), nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    cart_items: Mapped[list["Cart"]] = relationship("Cart", back_populates="product")


class Cart(Base):
    __tablename__ = "cart"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user: Mapped["User"] = relationship("User", back_populates="cart_items")
    product: Mapped["Product"] = relationship("Product", back_populates="cart_items")
