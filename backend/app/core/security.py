from datetime import datetime, timedelta
from typing import Optional
import secrets
import smtplib
from email.message import EmailMessage

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def generate_otp_code(length: int = 6) -> str:
    # 6-digit numeric OTP
    return "".join(str(secrets.randbelow(10)) for _ in range(length))


def send_otp_email(to_email: str, otp_code: str) -> None:
  
    msg = EmailMessage()
    msg["Subject"] = "StockMaster Password Reset OTP"
    msg["From"] = "no-reply@yourcompany.local"
    msg["To"] = to_email
    msg.set_content(f"Your OTP code is: {otp_code}. It is valid for 10 minutes.")

    # Uncomment and configure once you have SMTP:
    # with smtplib.SMTP("smtp.yourcompany.local", 25) as server:
    #     server.send_message(msg)

    # For now, you can just log it to console in dev:
    print(f"[DEV] OTP for {to_email}: {otp_code}")
