from decimal import Decimal
from typing import List
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request, Depends
from odmantic import ObjectId
from pydantic import BaseModel

from dependencies.oauth import oauth_check_dep
from dependencies.roles import role_customer
from globals import engine
from models import (Cart, CartItem, Payment, PaymentGateway, PaymentStatus, Order, OrderStatus, OrderItem,
                    Address, Product, ProductStatus)

router = APIRouter(prefix="/checkout", tags=["checkout"])


class ProductInfo(BaseModel):
    name: str
    thumbnail_url: str | None
    price: Decimal


class ItemBrief(CartItem):
    product: ProductInfo
    categories: List[str]


class SummaryResponse(BaseModel):
    cart_id: ObjectId
    items: List[ItemBrief]
    total_items: int
    amount: Decimal


@router.get("/summary", response_model=SummaryResponse, dependencies=[Depends(oauth_check_dep), Depends(role_customer)])
async def cart_summary(req: Request):
    user = req.state.user
    cart = await engine.find_one(Cart, Cart.user == user.id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    total_amount = 0
    items = []
    pending_remove = []
    for item in cart.items:
        product = await engine.find_one(Product, Product.id == item.product_id)
        if not product or product.status != ProductStatus.PUBLISHED or product.stock < item.quantity:
            # Remove invalid product from cart
            pending_remove.append(item)
            continue

        total_amount += product.price * item.quantity
        items.append(ItemBrief(
            product_id=product.id,
            product=ProductInfo(
                name=product.name,
                thumbnail_url=product.thumbnail_url,
                price=product.price
            ),
            quantity=item.quantity,
            categories=product.category_names
        ))

    if pending_remove:
        for item in pending_remove:
            cart.items.remove(item)

        await engine.save(cart)

    return SummaryResponse(
        cart_id=cart.id,
        amount=total_amount,
        total_items=len(items),
        items=items
    )


@router.get("/payments", response_model=List[PaymentGateway],
            dependencies=[Depends(oauth_check_dep), Depends(role_customer)])
async def payment_options(req: Request):
    user = req.state.user
    cart = await engine.find_one(Cart, Cart.user == user.id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")

    products = await engine.find(Product, Product.id.in_([item.product_id for item in cart.items]))

    total_amount = sum([product.price * item.quantity for product, item in zip(products, cart.items)])
    if total_amount == Decimal('0.00'):
        return [PaymentGateway.FREE]
    else:
        return [PaymentGateway.DUMMY_GATEWAY]


@router.post("/pay", response_model=dict, dependencies=[Depends(oauth_check_dep), Depends(role_customer)])
async def create_payment(
        req: Request,
        cart_id: ObjectId,
        address_id: ObjectId,
        gateway: PaymentGateway
):
    user = req.state.user
    order = await engine.find_one(Order, Order.id == cart_id, Order.user == user.id)
    if order and order.status != OrderStatus.PENDING_PAYMENT:
        raise HTTPException(status_code=400, detail="Order already processed")
    if not order:
        cart = await engine.find_one(Cart, Cart.id == cart_id, Cart.user == user.id)
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        address = await engine.find_one(Address, Address.id == address_id, Address.user == user.id)
        if not address:
            raise HTTPException(status_code=404, detail="Address not found")

        order_items = []
        total_amount = 0

        products = await engine.find(Product, Product.id.in_([item.product_id for item in cart.items]))

        for item in cart.items:
            product = next((p for p in products if p.id == item.product_id), None)
            if not product:
                continue

            if product.status != ProductStatus.PUBLISHED or product.stock < item.quantity:
                raise HTTPException(status_code=400, detail=f"One (or more) product is not available from cart")

            total_amount += product.price * item.quantity
            order_items.append(OrderItem(product_id=item.product_id, quantity=item.quantity))

        order = Order(
            id=cart_id,
            user=user,
            address=address,
            items=order_items,
            total_amount=total_amount,
        )
        await engine.save(order)

        # delete cart
        await engine.delete(cart)

    # Check if payment is required
    if order.total_amount != Decimal('0.00') and gateway == PaymentGateway.FREE:
        # old joke, let's see how many people get it instead of Googling it
        raise HTTPException(status_code=400, detail="Ah ah ah, you didn't say the magic word")

    # Get latest payment status from order
    if order.payments:
        last_payment = order.payments[-1]
        if last_payment.status == PaymentStatus.PENDING:
            # Cancel the previous payment
            last_payment.status = PaymentStatus.CANCELLED
            # Feature: Cancel payment based on gateway
            await engine.save(last_payment)

    payment = Payment(
        amount=order.total_amount,
        gateway=gateway,
        status=PaymentStatus.PENDING
    )

    # Add payment ID to order
    order.payments.append(payment)
    await engine.save(order)

    # Redirect based on payment gateway
    match gateway:
        case PaymentGateway.FREE:
            # No payment required, update order status now.
            payment.status = PaymentStatus.PAID
            order.expire_date = None  # Feature: Clear cron task
            order.status = OrderStatus.PROCESSING
            await engine.save(order)
            return {"redirect_url": f"/api/order/{cart_id}"}
        case PaymentGateway.DUMMY_GATEWAY:
            return {"redirect_url": f"/api/checkout/dummy-payment?order_id={order.id}"}
        case PaymentGateway.STRIPE:
            # TODO: Implement Stripe payment
            return {"redirect_url": f"/api/checkout/stripe-payment?order_id={order.id}"}


@router.get("/dummy-payment", status_code=302, dependencies=[Depends(oauth_check_dep), Depends(role_customer)])
async def dummy_payment(req: Request, order_id: ObjectId):
    # Build a dummy payment page
    user = req.state.user
    order = await engine.find_one(
        Order,
        Order.id == order_id,
        Order.user == user.id,
        Order.status == OrderStatus.PENDING_PAYMENT)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    payment = order.payments[-1]
    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(status_code=400, detail="Payment already processed")

    reference_id = f"dummy|{uuid4()}"

    redirect_url = "/api/checkout/callback?"
    redirect_url += f"&order_id={order_id}"
    redirect_url += f"&payment_status=paid"
    redirect_url += f"&reference_id={reference_id}"

    raise HTTPException(status_code=302, headers={"Location": redirect_url})


@router.get("/callback", status_code=204)
async def payment_callback(
        order_id: ObjectId,
        payment_status: PaymentStatus,
        reference_id: str = None
):
    order = await engine.find_one(
        Order,
        Order.id == order_id,
        Order.status == OrderStatus.PENDING_PAYMENT
    )

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Feature: Do gateway verify

    if payment_status == PaymentStatus.PAID:
        order.expire_date = None  # Feature: Clear cron task
        order.status = OrderStatus.PROCESSING

    last_payment = order.payments[-1]
    last_payment.status = PaymentStatus.FAILED if payment_status != PaymentStatus.PAID else PaymentStatus.PAID
    last_payment.reference_id = reference_id
    await engine.save(order)
