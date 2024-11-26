from fastapi import HTTPException, status, Request


def role_wrapper(role: str):
    async def wrapper(request: Request):
        if not request.state.user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="login first")

        if role not in request.state.user.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    return wrapper


role_customer = role_wrapper("customer")
role_admin = role_wrapper("admin")
