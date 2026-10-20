import re
from pydantic import BaseModel, EmailStr, field_validator


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("이름을 입력해주세요")
        if len(v) > 100:
            raise ValueError("이름은 100자를 초과할 수 없습니다")
        if not re.match(r"^[가-힣a-zA-Z\s]+$", v):
            raise ValueError("이름은 한글 또는 영문만 입력 가능합니다")
        return v.strip()

    @field_validator("email")
    @classmethod
    def validate_email_ascii(cls, v):
        local_part = v.split("@")[0]
        if not local_part.isascii():
            raise ValueError("이메일은 영문, 숫자, 특수문자만 입력 가능합니다")
        if len(local_part) > 64:
            raise ValueError("이메일 로컬 파트는 64자를 초과할 수 없습니다")
        if len(v) > 254:
            raise ValueError("이메일은 254자를 초과할 수 없습니다")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if not v or not v.strip():
            raise ValueError("비밀번호를 입력해주세요")
        if v != v.strip():
            raise ValueError("비밀번호 앞뒤에 공백을 포함할 수 없습니다")
        if len(v) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다")
        if len(v) > 255:
            raise ValueError("비밀번호는 255자를 초과할 수 없습니다")
        return v


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        local_part = v.split("@")[0]
        if len(local_part) > 64:
            raise ValueError("이메일 로컬 파트는 64자를 초과할 수 없습니다")
        if len(v) > 254:
            raise ValueError("이메일은 254자를 초과할 수 없습니다")
        return v.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) > 255:
            raise ValueError("비밀번호는 255자를 초과할 수 없습니다")
        return v


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


def validate_new_password(v: str) -> str:
    if not v or not v.strip():
        raise ValueError("비밀번호를 입력해주세요")
    if v != v.strip():
        raise ValueError("비밀번호 앞뒤에 공백을 포함할 수 없습니다")
    if len(v) < 8:
        raise ValueError("비밀번호는 8자 이상이어야 합니다")
    if len(v) > 255:
        raise ValueError("비밀번호는 255자를 초과할 수 없습니다")
    return v


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_pw(cls, v):
        return validate_new_password(v)


class PasswordResetRequest(BaseModel):
    email: EmailStr
    new_password: str

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v):
        return v.lower()

    @field_validator("new_password")
    @classmethod
    def validate_new_pw(cls, v):
        return validate_new_password(v)


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
