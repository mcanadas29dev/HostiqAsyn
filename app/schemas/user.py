
import uuid
from datetime import datetime
from typing import Literal

from fastapi_users import schemas


AuthProvider = Literal["local", "google"]
UserStatus = Literal["pending", "active", "blocked", "deleted"]


class UserRead(schemas.BaseUser[uuid.UUID]):
    nombre: str | None = None
    apellidos: str | None = None
    telefono: str | None = None

    auth_provider: AuthProvider
    email_verified_at: datetime | None = None
    status: UserStatus
    locale: str
    created_at: datetime
    updated_at: datetime


class UserCreate(schemas.BaseUserCreate):
    nombre: str | None = None
    apellidos: str | None = None
    telefono: str | None = None

    locale: str = "es"


class UserUpdate(schemas.BaseUserUpdate):
    nombre: str | None = None
    apellidos: str | None = None
    telefono: str | None = None
    locale: str | None = None
