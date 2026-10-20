from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
import models
import schemas
import auth as auth_utils

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserResponse, status_code=201)
def register(body: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == body.email).first():
        raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")
    user = models.User(
        name=body.name,
        email=body.email,
        password_hash=auth_utils.hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


MAX_FAILED_ATTEMPTS = 3


@router.post("/login", response_model=schemas.TokenResponse)
def login(body: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    if user.failed_attempts >= MAX_FAILED_ATTEMPTS:
        raise HTTPException(status_code=423, detail="비밀번호를 3회 이상 틀렸습니다. 비밀번호를 재설정해주세요.")

    if not auth_utils.verify_password(body.password, user.password_hash):
        user.failed_attempts += 1
        db.commit()
        remaining = MAX_FAILED_ATTEMPTS - user.failed_attempts
        if remaining <= 0:
            raise HTTPException(status_code=423, detail="비밀번호를 3회 이상 틀렸습니다. 비밀번호를 재설정해주세요.")
        raise HTTPException(status_code=401, detail=f"이메일 또는 비밀번호가 올바르지 않습니다. (남은 시도 횟수: {remaining}회)")

    user.failed_attempts = 0
    db.commit()
    token = auth_utils.create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout", status_code=200)
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(auth_utils.bearer_scheme),
    _: models.User = Depends(auth_utils.get_current_user),
):
    auth_utils.blacklist_token(credentials.credentials)
    return {"message": "로그아웃 되었습니다."}


@router.patch("/password", status_code=200)
def change_password(
    body: schemas.PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user),
):
    if not auth_utils.verify_password(body.current_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="현재 비밀번호가 올바르지 않습니다.")
    if auth_utils.verify_password(body.new_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="새 비밀번호가 현재 비밀번호와 동일합니다.")
    current_user.password_hash = auth_utils.hash_password(body.new_password)
    db.commit()
    return {"message": "비밀번호가 변경되었습니다."}


@router.post("/password/reset", status_code=200)
def reset_password(
    body: schemas.PasswordResetRequest,
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="존재하지 않는 이메일입니다.")
    if user.failed_attempts < MAX_FAILED_ATTEMPTS:
        raise HTTPException(status_code=403, detail="비밀번호 재설정은 3회 이상 실패한 경우에만 가능합니다.")
    user.password_hash = auth_utils.hash_password(body.new_password)
    user.failed_attempts = 0
    db.commit()
    return {"message": "비밀번호가 재설정되었습니다."}
