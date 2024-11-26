from hashlib import md5
from typing import Optional

import jwt
from fastapi import HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

from odmantic.bson import ObjectId
from globals import engine, SECRET_KEY, ALGORITHM
from models import User


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: str
    session: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user_by_id(user_id: str) -> Optional[User]:
    return await engine.find_one(User, User.id == ObjectId(user_id))


async def oauth_check_dep(request: Request):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid Session",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = await oauth2_scheme(request)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("extra", {}).get("id")
        session: str = payload.get("jti")
        if user_id is None or session is None:
            raise credentials_exception
        token_data = TokenData(id=user_id, session=session)
    except InvalidTokenError:
        raise credentials_exception

    user = await get_user_by_id(token_data.id)

    if user is None:
        raise credentials_exception
    # Check for password change
    if md5(user.password_hash.encode()).hexdigest() != token_data.session:
        raise credentials_exception

    request.state.user = user
