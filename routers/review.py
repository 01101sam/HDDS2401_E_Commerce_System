import datetime
from typing import Optional, List

from fastapi import APIRouter, HTTPException, Depends, Request, Body
from odmantic import ObjectId
from pydantic import BaseModel

from dependencies.roles import role_admin
from globals import engine
from models import Review, Product, OrderStatus, Order, ProductStatus

router = APIRouter(prefix="/reviews", tags=["reviews"])
count_map = ["one", "two", "three", "four", "five"]


class ReviewCreate(BaseModel):
    product_id: ObjectId

    rating: int = Body(ge=1, le=5)
    comment: Optional[str] = None


class CanReviewRequest(BaseModel):
    product_id: ObjectId


class CanReviewResponse(BaseModel):
    qualified: bool


class ReviewResponse(BaseModel):
    full_name: str
    thumbnail_url: Optional[str] = None
    rating: int
    comment: Optional[str] = None
    created_at: datetime.datetime


async def user_qualified_for_review(user_id: ObjectId, product_id: ObjectId):
    orders = await engine.find(
        Order,
        Order.user == user_id,
        Order.status == OrderStatus.COMPLETED,
        {"items.product_id": product_id},
        {"items.review_id": None}
    )

    return len(orders) > 0


async def get_order_by_qualification(user_id: ObjectId, product_id: ObjectId):
    orders = await engine.find(
        Order,
        Order.user == user_id,
        Order.status == OrderStatus.COMPLETED,
        {"items.product_id": product_id},
        {"items.review_id": None}
    )

    return orders[0] if len(orders) > 0 else None


def calculate_average_rating(product: Product):
    product.rating.average = sum(
        (i + 1) * getattr(product.rating, f"{count_map[i]}_star_count") for i in range(5)
    ) / sum(getattr(product.rating, f"{count_map[i]}_star_count") for i in range(5))


@router.post("", status_code=201)
async def create_review(req: Request, review: ReviewCreate):
    user = req.state.user
    product: Product = await engine.find_one(
        Product,
        Product.id == review.product_id,
        Product.status == ProductStatus.PUBLISHED)
    if not user or not product:
        raise HTTPException(status_code=404, detail="User or Product not found")

    # Check has the user already reviewed the product
    if not await user_qualified_for_review(user.id, review.product_id):
        raise HTTPException(status_code=400, detail="not qualified for review")

    new_review = Review(user=user, product=product, rating=review.rating, comment=review.comment)
    await engine.save(new_review)

    product.reviews.append(new_review.id)

    count_str = count_map[review.rating - 1]
    # add the new review to the count_map
    setattr(product.rating, f"{count_str}_star_count", getattr(product.rating, f"{count_str}_star_count") + 1)

    # calculate the average rating
    calculate_average_rating(product)

    order = await get_order_by_qualification(user.id, review.product_id)
    if order:
        order_item = next(filter(lambda x: x.product_id == product.id, order.items))
        order_item.review_id = new_review.id
        await engine.save(order)

    await engine.save(product)


@router.get("/can-review", response_model=CanReviewResponse)
async def can_review(req: Request, product_id: ObjectId):
    user = req.state.user
    return CanReviewResponse(qualified=await user_qualified_for_review(user.id, product_id))


@router.get("/{product_id}", response_model=List[ReviewResponse], dependencies=[Depends(role_admin)])
async def read_review(product_id: ObjectId):
    reviews = await engine.find(Review, Review.product == product_id)

    item = []

    for review in reviews:
        item.append(ReviewResponse(
            full_name=review.user.first_name + (f" {review.user.last_name}" if review.user.last_name else ""),
            thumbnail_url=review.user.thumbnail_url,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at
        ))

    return item


@router.delete("/{review_id}", status_code=204, dependencies=[Depends(role_admin)])
async def delete_review(review_id: ObjectId):
    review = await engine.find_one(Review, Review.id == review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    product = await engine.find_one(Product, Product.id == review.product.id)
    if product:
        product.reviews.remove(review.id)

        count_str = count_map[review.rating - 1]
        # remove the review from the count_map
        setattr(product.rating, f"{count_str}_star_count", getattr(product.rating, f"{count_str}_star_count") - 1)

        # calculate the average rating
        calculate_average_rating(product)
        await engine.save(product)

    await engine.delete(review)
