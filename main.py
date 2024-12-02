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


app = FastAPI(
    debug=False,
    lifespan=lifespan,
    root_path="/api",
    redoc_url=None,
)

# region Catch all exceptions
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse("", status_code=400)


# endregion Catch all exceptions


app.add_middleware(GZipMiddleware, minimum_size=1024, compresslevel=5)  # noqa
app.include_router(media.router)
app.include_router(auth.router)
app.include_router(checkout.router)

for router in (
        product.router, order.router, review.router, category.router,
        cart.router, account.router, shipping.router, address.router,
):
    app.include_router(router, dependencies=[Depends(oauth_check_dep), Depends(role_customer)])

for router in (
        user.router,
):
    app.include_router(router, dependencies=[Depends(oauth_check_dep), Depends(role_admin)])
