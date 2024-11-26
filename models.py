import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List

from odmantic import EmbeddedModel, Reference
from odmantic import Field, Model
from odmantic.bson import ObjectId
from pydantic import EmailStr, condecimal

from globals import engine


class Role(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class PhoneNumber(EmbeddedModel):
    country_code: int = Field(ge=1, le=999)
    number: str


class User(Model):
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))

    # Auth
    # For guest: Name would be "Guest_1X" (where 1X is unix nano) as a placeholder
    first_name: str
    last_name: Optional[str] = None
    thumbnail_url: Optional[str] = None
    # Guest user will leave email and password_hash empty
    email: EmailStr = Field(unique=True)
    password_hash: str

    # Permissions
    roles: List[Role] = Field(default=[Role.CUSTOMER])


class Address(Model):
    user: User = Reference()

    street1: str
    street2: Optional[str] = None
    city: str
    state: str
    country: str

    zip_code: Optional[str] = None

    phone_number: PhoneNumber


class Category(Model):
    name: str = Field(unique=True)
    logo_id: Optional[str] = None

    product_ids: List[ObjectId] = Field(default=[])


class ProductStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class ProductRating(EmbeddedModel):
    average: int = Field(default=5, ge=1, le=5)

    one_star_count: int = Field(default=0, ge=0)
    two_star_count: int = Field(default=0, ge=0)
    three_star_count: int = Field(default=0, ge=0)
    four_star_count: int = Field(default=0, ge=0)
    five_star_count: int = Field(default=0, ge=0)


class Product(Model):
    sku: str = Field(unique=True)
    name: str = Field(index=True)
    description_html: Optional[str] = None

    thumbnail_url: Optional[str] = None
    media_url: Optional[str] = None

    category_names: List[str]

    price: condecimal = Field(default=Decimal('0.00'), ge=0)
    # A.K.A Keywords
    tags: List[str] = Field(default=[])

    reviews: List[ObjectId] = Field(default=[])
    rating: ProductRating = Field(default_factory=ProductRating)

    stock: int = 0
    status: ProductStatus = ProductStatus.DRAFT


class OrderStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    PROCESSING = "processing"
    DELIVERING = "delivering"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    __transitions__ = {
        PENDING_PAYMENT: {PROCESSING, CANCELLED},
        PROCESSING: {DELIVERING, COMPLETED, CANCELLED},
        DELIVERING: {COMPLETED, CANCELLED},
        COMPLETED: set(),  # No transitions allowed from DELIVERED
        CANCELLED: set(),  # No transitions allowed from CANCELLED
    }

    def can_transition_to(self, new_status):
        """Check if the transition to the new status is allowed."""
        return new_status in self.__transitions__[self]  # noqa


class OrderItem(EmbeddedModel):
    product_id: ObjectId
    quantity: int = Field(default=1, ge=1)

    review_id: Optional[ObjectId] = None


class PaymentGateway(str, Enum):
    DUMMY_GATEWAY = "dummy_gateway"
    FREE = "free"
    STRIPE = "stripe"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    EXPIRED = "expired"
    REFUNDED = "refunded"
    FAILED = "failed"
    CANCELLED = "cancelled"

    __transitions__ = {
        PENDING: {PAID, EXPIRED, FAILED},
        PAID: {REFUNDED},  # No transitions allowed from PAID
        EXPIRED: set(),  # No transitions allowed from EXPIRED
        FAILED: set(),  # No transitions allowed from FAILED
        CANCELLED: set(),  # No transitions allowed from CANCELLED
    }

    def can_transition_to(self, new_status):
        """Check if the transition to the new status is allowed."""
        return new_status in self.__transitions__[self]  # noqa


class Payment(EmbeddedModel):
    # Feature: Add expire timer
    amount: condecimal = Field(default=Decimal('0.00'), ge=0)

    gateway: PaymentGateway
    reference_id: Optional[str] = None
    metadata: Optional[dict] = Field(default={})

    status: PaymentStatus = PaymentStatus.PENDING


class ShippingCarrier(str, Enum):
    ASSIGN_PENDING = "assign_pending"
    MANUAL = "manual"
    SF_EXPRESS = "sf_express"
    DHL = "dhl"
    KERRY_LOGISTICS = "kerry_logistics"
    # Morning Express
    MECHK = "mechk"


class ShippingStatus(str, Enum):
    PENDING = "pending"
    PENDING_PICKUP = "pending_pickup"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

    __transitions__ = {
        PENDING: {PENDING_PICKUP, CANCELLED},
        PENDING_PICKUP: {SHIPPED, CANCELLED},
        SHIPPED: {DELIVERED, CANCELLED},
        DELIVERED: set(),  # No transitions allowed from DELIVERED
        CANCELLED: set(),  # No transitions allowed from CANCELLED
    }

    def can_transition_to(self, new_status):
        """Check if the transition to the new status is allowed."""
        return new_status in self.__transitions__[self]  # noqa


class Shipping(EmbeddedModel):
    shipping_carrier: ShippingCarrier = ShippingCarrier.ASSIGN_PENDING
    tracking_number: Optional[str] = None

    status: ShippingStatus = ShippingStatus.PENDING


class Order(Model):
    user: User = Reference()
    address: Address = Reference()

    items: List[OrderItem] = Field(default=[])
    total_amount: condecimal = Field(default=Decimal('0.00'), ge=0)
    # Not for each item, it's for the whole order, this is just payment history
    payments: List[Payment] = Field(default=[])
    shipping: Shipping = Field(default_factory=Shipping)

    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))
    # Feature: Order needs to be cancelled when order is unpaid over 24 hours
    expire_date: Optional[datetime.datetime] = Field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=24)
    )
    status: OrderStatus = OrderStatus.PENDING_PAYMENT


class Review(Model):
    user: User = Reference()
    product: Product = Reference()
    rating: int = Field(default=5, ge=1, le=5)

    comment: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))


class CartItem(EmbeddedModel):
    product_id: ObjectId
    quantity: int = Field(default=1, ge=1)


class Cart(Model):
    user: User = Reference()
    items: List[CartItem] = Field(default=[])

    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))


async def init_database():
    await engine.configure_database([
        User,
        Address,
        Category,
        Product,
        Order,
        Review,
        Cart,
    ])
