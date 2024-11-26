from typing import List

from fastapi import APIRouter, HTTPException
from odmantic import ObjectId
from pydantic import BaseModel
from typing_extensions import Optional

from dependencies.oauth import get_password_hash
from globals import engine
from models import User

router = APIRouter(prefix="/users", tags=["users"])


class FindRequest(BaseModel):
    user_id: ObjectId | None = None
    email: str | None = None


class UpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    thumbnail_url: Optional[str] = None

    email: Optional[str] = None
    password: Optional[str] = None
    roles: Optional[List[str]] = None


@router.get("", response_model=List[User])
async def get_all_users():
    return await engine.find(User)


@router.post("/find")
async def find_user(request: FindRequest):
    if not request.user_id and not request.email:
        raise HTTPException(status_code=400, detail="You must provide either user_id or email")

    result = None
    try:
        if request.user_id:
            result = await engine.find_one(User, User.id == request.user_id)
        elif request.email:
            result = await engine.find_one(User, User.email == request.email)

        if not result:
            raise HTTPException(status_code=404, detail="User not found")

        return result
    except Exception:
        raise HTTPException(status_code=404, detail="User not found")


@router.put("/{user_id}", status_code=204)
async def update_user(user_id: ObjectId, user_data: UpdateRequest):
    user = await engine.find_one(User, User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.model_update(user_data)

    if user_data.password:
        user.password_hash = get_password_hash(user_data.password)

    if type(user_data.last_name) == str and not user_data.last_name:
        user.last_name = None

    if type(user_data.thumbnail_url) == str and not user_data.thumbnail_url:
        user.thumbnail_url = None

    await engine.save(user_data)


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: ObjectId):
    user = await engine.find_one(User, User.id == user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await engine.delete(user)
