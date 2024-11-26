from typing import Optional

from fastapi import APIRouter, HTTPException, Request, Depends
from odmantic import ObjectId
from pydantic import BaseModel

from dependencies.roles import role_admin
from globals import engine
from models import Order, Shipping, ShippingStatus, User, ShippingCarrier, OrderStatus

router = APIRouter(prefix="/shipping", tags=["shipping"])


class CarrierUpdateRequest(BaseModel):
    shipping_carrier: ShippingCarrier
    tracking_number: Optional[str] = None


class StatusUpdateRequest(BaseModel):
    status: ShippingStatus


async def get_shipping_by_order(order_id: ObjectId, user: Optional[User] = None):
    if user:
        order = await engine.find_one(Order, Order.id == order_id, Order.user == user.id)
    else:
        order = await engine.find_one(Order, Order.id == order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order, order.shipping


@router.get("/{order_id}", response_model=Shipping)
async def get_shipping(req: Request, order_id: ObjectId):
    user = req.state.user
    _, shipping = await get_shipping_by_order(order_id, user)

    return shipping


@router.patch("/{order_id}/carrier", status_code=204, dependencies=[Depends(role_admin)])
async def update_shipping_carrier(order_id: ObjectId, req: CarrierUpdateRequest):
    order, shipping = await get_shipping_by_order(order_id)

    shipping.model_update(req)
    await engine.save(order)


@router.patch("/{order_id}/tracking", status_code=204, dependencies=[Depends(role_admin)])
async def update_shipping_tracking(order_id: ObjectId, tracking_number: str):
    order, shipping = await get_shipping_by_order(order_id)

    shipping.tracking_number = tracking_number
    await engine.save(order)


@router.patch("/{order_id}/status", status_code=204, dependencies=[Depends(role_admin)])
async def update_shipping_status(order_id: ObjectId, req: StatusUpdateRequest):
    order, shipping = await get_shipping_by_order(order_id)

    if not shipping.status.can_transition_to(req.status):
        raise HTTPException(status_code=400, detail="Invalid status transition")

    shipping.status = req.status

    match shipping.status:
        case ShippingStatus.SHIPPED:
            order.status = OrderStatus.DELIVERING
        case ShippingStatus.DELIVERED:
            order.status = OrderStatus.COMPLETED
        case ShippingStatus.CANCELLED:
            order.status = OrderStatus.CANCELLED

    await engine.save(order)
