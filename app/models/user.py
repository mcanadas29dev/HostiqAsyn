
from datetime import datetime

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "user"

    __table_args__ = (
        CheckConstraint(
            "auth_provider IN ('local', 'google')",
            name="ck_user_auth_provider",
        ),
        CheckConstraint(
            "status IN ('pending', 'active', 'blocked', 'deleted')",
            name="ck_user_status",
        ),
    )

    # Datos personales
    nombre: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    apellidos: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    telefono: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    # Proveedor de autenticación
    auth_provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="local",
        server_default=text("'local'"),
    )

    # Verificación del correo electrónico
    email_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    # Estado funcional de la cuenta
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default=text("'pending'"),
    )

    # Idioma preferido
    locale: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="es",
        server_default=text("'es'"),
    )

    # Auditoría
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
