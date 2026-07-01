from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from auth import get_current_user
from color_utils import (
    recommend_colors,
    extract_dominant_color,
    ALLOWED_CONTENT_TYPES,
    MAX_IMAGE_SIZE,
)
import schemas
import models

router = APIRouter(prefix="/colors", tags=["colors"])


@router.post("/extract", response_model=schemas.ColorExtractResponse)
async def extract_color(
    file: UploadFile = File(...),
    _: models.User = Depends(get_current_user),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="지원하지 않는 이미지 형식입니다. (jpg, png, webp만 허용)")

    contents = await file.read()

    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="이미지 크기는 10MB를 초과할 수 없습니다.")

    try:
        extracted_hex = extract_dominant_color(contents)
    except Exception:
        raise HTTPException(status_code=422, detail="이미지를 처리할 수 없습니다.")

    recommendations = recommend_colors(extracted_hex)

    return schemas.ColorExtractResponse(
        extracted_color=extracted_hex,
        recommendations=recommendations,
    )


