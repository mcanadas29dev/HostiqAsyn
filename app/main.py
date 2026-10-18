from fastapi import FastAPI

from app.config import settings
from app.schemas import UserCreate, UserRead, UserUpdate
from app.users import auth_backend, fastapi_users

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

# Rutas de autenticación JWT: POST /auth/jwt/login
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# Rutas de registro, reset, verificación
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

# Rutas de usuario: GET/PATCH/DELETE /users/me
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}