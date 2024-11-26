from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr

from dependencies.oauth import pwd_context
from globals import engine
from models import User

router = APIRouter(prefix="/account", tags=["account"])


class UpdatePasswordRequest(BaseModel):
    old: str
    new: str


class UpdateEmailRequest(BaseModel):
    email: EmailStr


class UpdateNameRequest(BaseModel):
    first: str
    last: Optional[str] = None


@router.get("/me", response_model=User)
async def get_me(request: Request):
    user = request.state.user

    del user.id
    del user.password_hash
    del user.created_at
    del user.updated_at

    return user


# Update user password
@router.put("/password", status_code=204)
async def update_password(pwd_req: UpdatePasswordRequest, request: Request):
    user = request.state.user

    if not pwd_context.verify(pwd_req.old, user.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    user.password_hash = pwd_context.hash(pwd_req.new)
    await engine.save(user)


@router.put("/email", status_code=204)
async def update_email(request: UpdateEmailRequest, req: Request):
    user = req.state.user

    user.email = request.email
    await engine.save(user)


@router.put("/name", status_code=204)
async def update_name(request: UpdateNameRequest, req: Request):
    user = req.state.user

    user.first_name = request.first
    user.last_name = request.last
    await engine.save(user)
