from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    generate_otp_code,
    send_otp_email,
)
from app.models.inventory import User, PasswordResetToken

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    otp_code: str
    new_password: str



@router.post("/signup", response_model=UserOut, status_code=201)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    """
    Create a new user account.
    """
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=get_password_hash(payload.password),
        role="manager",  
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


#  Login with email + password.
#     Returns JWT access_token.
#     Frontend can store it and redirect to dashboard.
@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
   
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return TokenResponse(access_token=access_token)

#  Generate OTP and email it to the user. response is the same whether user exists or not.
@router.post("/request-password-reset")
def request_password_reset(
    payload: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    
    user = db.query(User).filter(User.email == payload.email).first()

    if user:
        otp = generate_otp_code()
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        token_entry = PasswordResetToken(
            user_id=user.id,
            otp_code=otp,
            expires_at=expires_at,
            used=False,
            created_at=datetime.utcnow(),
        )
        db.add(token_entry)
        db.commit()
        # Send email (or log to console in dev)
        send_otp_email(user.email, otp)

    return {"message": "If this email is registered, an OTP has been sent."}


@router.post("/reset-password")
def reset_password(
    payload: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
   
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or OTP")

    token_entry = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.otp_code == payload.otp_code,
            PasswordResetToken.used == False,  # noqa
            PasswordResetToken.expires_at >= datetime.utcnow(),
        )
        .order_by(PasswordResetToken.created_at.desc())
        .first()
    )

    if not token_entry:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    
    token_entry.used = True

    user.password_hash = get_password_hash(payload.new_password)

    db.add(user)
    db.add(token_entry)
    db.commit()

    return {"message": "Password has been reset successfully."}

#Get current loggedin user using JWT.
@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)):
  
    return current_user
