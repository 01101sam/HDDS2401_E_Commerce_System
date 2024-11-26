# list cart item
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Request, Query, HTTPException
from odmantic import ObjectId
from pydantic import BaseModel

from globals import engine
from models import Cart, CartItem, Product, ProductStatus

router = APIRouter(prefix="/cart", tags=["cart"])


class ProductInfo(BaseModel):
    name: str
    thumbnail_url: str | None
    price: Decimal


class ItemBrief(CartItem):
    product: ProductInfo


@router.get("", response_model=List[ItemBrief])
async def read_cart(req: Request):
    user = req.state.user
    cart = await engine.find_one(Cart, Cart.user == user.id)
    if cart is None:
        return []

    items = []
    pending_remove = []
    for item in cart.items:
        product = await engine.find_one(Product, Product.id == item.product_id)
        if product is None or product.status != ProductStatus.PUBLISHED or product.stock < item.quantity:
            # Remove from cart
            pending_remove.append(item.product_id)
            continue
        items.append(ItemBrief(
            product_id=product.id,
            quantity=item.quantity,
            product=ProductInfo(
                name=product.name, thumbnail_url=product.thumbnail_url, price=product.price
            )))

    if pending_remove:
        cart.items = [item for item in cart.items if item.product_id not in pending_remove]
        await engine.save(cart)

    return items


@router.patch("/{product_id}", status_code=204)
async def update_cart_qty(req: Request, product_id: ObjectId, qty: int = Query(ge=1, le=100)):
    user = req.state.user

    product = await engine.find_one(Product, Product.id == product_id and Product.status == ProductStatus.PUBLISHED)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    if product.stock < qty:
        raise HTTPException(status_code=400, detail="not enough stock")

    cart = await engine.find_one(Cart, Cart.user == user.id)
    if cart is None:
        cart = Cart(user=user)

    for item in cart.items:
        if item.product_id == product_id:
            item.quantity = qty
            await engine.save(cart)
            return None

    cart.items.append(CartItem(product_id=product_id, quantity=qty))
    await engine.save(cart)


@router.delete("/{product_id}", status_code=204)
async def delete_cart_item(req: Request, product_id: ObjectId):
    user = req.state.user
    cart = await engine.find_one(Cart, Cart.user == user.id)
    if cart is None:
        return None

    for idx, item in enumerate(cart.items):
        if item.product_id == product_id:
            del cart.items[idx]
            await engine.save(cart)
            break

    if len(cart.items) == 0:
        await engine.delete(cart)

    return None
