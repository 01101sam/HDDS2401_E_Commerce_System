from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Request
from odmantic import ObjectId
from odmantic.exceptions import DuplicateKeyError
from pydantic import BaseModel

from dependencies.roles import role_admin
from globals import engine
from models import Product, Category, Review, ProductStatus

router = APIRouter(prefix="/products", tags=["products"])


class UpdateProductRequest(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    description_html: Optional[str] = None

    thumbnail_url: Optional[str] = None
    media_url: Optional[str] = None

    category_names: Optional[List[str]] = None

    price: Optional[Decimal] = None
    tags: Optional[List[str]] = None

    stock: Optional[int] = None
    status: Optional[ProductStatus] = None


# Create a new product
@router.post("", response_model=Product, status_code=201, dependencies=[Depends(role_admin)])
async def create_product(product: Product):
    try:
        await engine.save(product)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Product already exists")

    # Update category
    for name in product.category_names:
        category = await engine.find_one(Category, Category.name == name)
        if not category:
            # Create if not exist
            category = Category(name=name)
            await engine.save(category)

        category.product_ids.append(product.id)
        await engine.save(category)

    return product


# Read a product by ID
@router.get("/{product_id}", response_model=Product)
async def read_product(product_id: ObjectId, req: Request):
    product = await engine.find_one(Product, Product.id == product_id)
    if not product or (product.status == ProductStatus.DRAFT and "admin" not in req.state.user.roles):
        raise HTTPException(status_code=404, detail="Product not found")

    return product


# Read all products
@router.get("", response_model=List[Product])
async def read_products(req: Request):
    return await engine.find(
        Product,
        Product.status == ProductStatus.PUBLISHED if "admin" not in req.state.user.roles else {}
    )


# Update a product by ID
@router.put("/{product_id}", status_code=204, dependencies=[Depends(role_admin)])
async def update_product(product_id: ObjectId, product_data: UpdateProductRequest):
    product = await engine.find_one(Product, Product.id == product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.model_update(product_data)
    await engine.save(product)

    # Handle category changes
    if product_data.category_names:
        categories = await engine.find(Category)
        for category in categories:
            if product_id in category.product_ids and category.name not in product_data.category_names:
                category.product_ids.remove(product_id)
            elif product_id not in category.product_ids and category.name in product_data.category_names:
                category.product_ids.append(product_id)

        await engine.save_all(categories)


# Delete a product by ID
@router.delete("/{product_id}", status_code=204, dependencies=[Depends(role_admin)])
async def delete_product(product_id: ObjectId):
    product = await engine.find_one(Product, Product.id == product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Remove from categories
    for name in product.category_names:
        category = await engine.find_one(Category, Category.name == name)
        if category:
            category.product_ids.remove(product_id)
            await engine.save(category)

    # reviews
    await engine.delete_all(await engine.find(Review, Review.product_id == product_id))

    await engine.delete(product)
