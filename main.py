from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.gzip import GZipMiddleware

from dependencies.oauth import oauth_check_dep
from dependencies.roles import role_customer, role_admin
from routers import user, product, order, auth, review, category
from routers.frontend import cart, account, shipping, address, checkout, media


@asynccontextmanager
async def lifespan(_: FastAPI):
    from models import init_database

    await init_database()
    yield


# app = FastAPI(debug=True, lifespan=lifespan)
app = FastAPI(debug=True)
app.add_middleware(GZipMiddleware, minimum_size=1024, compresslevel=5)  # noqa
app.include_router(auth.router)
app.include_router(checkout.router)

for router in (
        product.router,order.router,review.router,category.router,
        cart.router, account.router, shipping.router, address.router,
        media.router,
):
    app.include_router(router, dependencies=[Depends(oauth_check_dep), Depends(role_customer)])

for router in (
        user.router,
):
    app.include_router(router, dependencies=[Depends(oauth_check_dep), Depends(role_admin)])
