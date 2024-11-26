from typing import List

from fastapi import APIRouter, HTTPException, Request
from odmantic import ObjectId
from pydantic import BaseModel

from globals import engine
from models import Address

router = APIRouter(prefix="/address", tags=["address"])


class AddressModel(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str


@router.post("", status_code=201)
async def create_address(address: AddressModel, req: Request):
    user = req.state.user
    new_address = Address(**address.model_dump())
    new_address.user = user
    await engine.save(new_address)


@router.get("", response_model=List[Address])
async def read_addresses(req: Request):
    user = req.state.user
    addresses = await engine.find(Address, Address.user == user.id)
    for address in addresses:
        del address.user
    return addresses


@router.get("/{address_id}", response_model=Address)
async def read_address(address_id: ObjectId, req: Request):
    user = req.state.user
    address = await engine.find_one(Address, Address.id == address_id and Address.user == user.id)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    del address.user

    return address


@router.put("/{address_id}", status_code=204)
async def update_address(address_id: ObjectId, address: AddressModel, req: Request):
    user = req.state.user
    existing_address = await engine.find_one(Address, Address.id == address_id and Address.user == user.id)
    if existing_address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    updated_address = existing_address.model_copy(update=address.model_dump())
    await engine.save(updated_address)


@router.delete("/{address_id}", status_code=204)
async def delete_address(address_id: ObjectId, req: Request):
    user = req.state.user
    address = await engine.find_one(Address, Address.id == address_id and Address.user == user.id)
    if address is None:
        raise HTTPException(status_code=404, detail="Address not found")
    await engine.delete(address)
