import random
import string
from datetime import datetime, timedelta, timezone
from hashlib import md5
from typing import Optional

import jwt
from fastapi import HTTPException, status, APIRouter
from odmantic.exceptions import DuplicateKeyError
from pydantic import BaseModel, EmailStr

from dependencies.oauth import get_password_hash, pwd_context
from globals import (engine, ACCESS_TOKEN_EXPIRE_MINUTES, REMEMBER_ME_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM,
                     ALLOW_REGISTRATION, ALLOW_CHANGE_PASSWORD)
from models import User, Address, PhoneNumber

router = APIRouter(prefix="/auth", tags=["auth"])


class Token(BaseModel):
    access_token: str
    token_type: str


# region Request Models

class RegisterRequest(BaseModel):
    first_name: str
    last_name: Optional[str] = None

    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class ResetPasswordRequest(BaseModel):
    email: EmailStr


# endregion Request Models

# region Helper Functions


def verify_password(plain_password, password_hash):
    return pwd_context.verify(plain_password, password_hash)


async def get_user_by_email(email: str) -> Optional[User]:
    return await engine.find_one(User, User.email == email)


async def authenticate_user(email: str, password: str):
    user = await get_user_by_email(email)
    if not user or not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# create_access_token authenticate_user get_password_hash

# endregion Helper Functions

@router.post("/login", response_model=Token)
async def login_for_access_token(
        request: LoginRequest
) -> Token:
    user = await authenticate_user(request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expire_minutes = REMEMBER_ME_EXPIRE_MINUTES if request.remember_me else ACCESS_TOKEN_EXPIRE_MINUTES
    access_token_expires = timedelta(minutes=expire_minutes)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "jti": md5(user.password_hash.encode()).hexdigest(),
            "extra": {
                "id": str(user.id),
                "roles": user.roles
            },
        }, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register", status_code=201, response_model=User)
async def register_user(request: RegisterRequest):
    if not ALLOW_REGISTRATION:
        raise HTTPException(status_code=403, detail="Registration is disabled")

    user = User(
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        password_hash=get_password_hash(request.password)
    )

    try:
        await engine.save(user)

        address = Address(
            user=user,
            street1="123 Example Road",
            city="Central",
            state="Hong Kong",
            country="Hong Kong",
            phone_number=PhoneNumber(
                country_code=852,
                number="12345678"
            )
        )
        await engine.save(address)

        del user.password_hash
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="User already registered")

    return user


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    if not ALLOW_CHANGE_PASSWORD:
        raise HTTPException(status_code=403, detail="Password reset is disabled")

    user = await get_user_by_email(request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Feature: Send a password reset email
    # This is a demo app, so just reset with random password
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    user.password_hash = get_password_hash(new_password)
    await engine.save(user)

    raise HTTPException(status_code=200, detail=f"Password reset successfully, your new password is: {new_password}")
