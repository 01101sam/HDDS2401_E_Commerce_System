# Display all products
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Request
from odmantic.exceptions import DuplicateKeyError
from pydantic import BaseModel

from dependencies.roles import role_admin
from globals import engine
from models import Category, Product, ProductStatus

router = APIRouter(prefix="/categories", tags=["categories"])


class CategoryCreate(BaseModel):
    name: str


# Read all categories
@router.get("", response_model=List[Category])
async def read_categories():
    categories = await engine.find(Category)

    for category in categories:
        del category.product_ids

    return categories

# Create a new category
@router.post("", status_code=201, dependencies=[Depends(role_admin)])
async def create_category(request: CategoryCreate):
    try:
        category = Category(name=request.name)

        await engine.save(category)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="Category already exists")


# Read a category by ID
@router.get("/{category_name}", response_model=Category)
async def read_category(category_name: str):
    category = await engine.find_one(Category, Category.name == category_name)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.get("/{category_name}/products", response_model=List[Product])
async def list_category_products(category_name: str, req: Request):
    user = req.state.user
    category = await engine.find_one(Category, Category.name == category_name)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return await engine.find(Product, Product.id.in_(category.product_ids) & (
            Product.status == ProductStatus.PUBLISHED or user.role == "admin"
    ))


# Update a category by ID
@router.put("/{category_name}", status_code=204, dependencies=[Depends(role_admin)])
async def update_category(category_name: str, category_data: Category):
    category = await engine.find_one(Category, Category.name == category_name)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category_data.id = category.id
    await engine.save(category_data)


# Delete a category by ID
@router.delete("/{category_name}", status_code=204, dependencies=[Depends(role_admin)])
async def delete_category(category_name: str):
    category = await engine.find_one(Category, Category.name == category_name)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await engine.delete(category)
