from typing import List

from fastapi import APIRouter, HTTPException, Depends, Request
from odmantic import ObjectId

from dependencies.roles import role_admin
from globals import engine
from models import Order, OrderStatus

router = APIRouter(prefix="/order", tags=["order"])


# Read all orders
@router.get("/me", response_model=List[Order])
async def read_my_orders(req: Request):
    user = req.state.user
    orders = await engine.find(Order, Order.user == user.id)

    for order in orders:
        del order.user
        del order.address.user

    return orders


@router.get("/all", response_model=List[Order], dependencies=[Depends(role_admin)])
async def read_all_orders():
    orders = await engine.find(Order)

    for order in orders:
        del order.user.password_hash
        del order.address.user

    return orders


# Read an order by ID
@router.get("/{order_id}", response_model=Order)
async def read_order(order_id: ObjectId, req: Request):
    user = req.state.user
    order = await engine.find_one(
        Order,
        Order.id == order_id and (Order.user == user.id or user.role == "admin")
    )

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    del order.user
    del order.address.user
    return order


# Update an order by ID
@router.patch("/{order_id}/status", status_code=204, dependencies=[Depends(role_admin)])
async def update_order(order_id: ObjectId, order_status: OrderStatus):
    order = await engine.find_one(Order, Order.id == order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if not order_status.can_transition_to(order.status):
        raise HTTPException(status_code=400, detail="Invalid status transition")

    order.status = order_status
    await engine.save(order)


# Delete an order by ID
@router.delete("/{order_id}", status_code=204, dependencies=[Depends(role_admin)])
async def delete_order(order_id: ObjectId):
    order = await engine.find_one(Order, Order.id == order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    await engine.delete(order)
