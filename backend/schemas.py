from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProductResponse(BaseModel):
    id: int
    name: str
    gender: str
    category: str
    subcategory: str
    color_name: str
    hex: str
    price: int
    model_config = {"from_attributes": True}


class ProductListResponse(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int
    items: list[ProductResponse]


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr
    new_password: str


class ColorRecommendation(BaseModel):
    color_name: str
    hex: str


class ColorExtractResponse(BaseModel):
    extracted_color: str
    recommendations: list[ColorRecommendation]


class CartItemCreate(BaseModel):
    product_id: int


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product: ProductResponse
    model_config = {"from_attributes": True}
