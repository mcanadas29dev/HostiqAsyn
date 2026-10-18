import uuid
from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.jwt import generate_jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_async_session
from app.email import send_email
from app.models import User


# ---------- Database adapter ----------

async def get_user_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    yield SQLAlchemyUserDatabase(session, User)


# ---------- UserManager ----------

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.reset_password_token_secret
    verification_token_secret = settings.verification_token_secret

    async def on_after_register(
        self, user: User, request=None
    ) -> None:
        # Enviar email de verificación automáticamente al registrarse
        await self._send_verification_email(user)

    async def on_after_forgot_password(
        self, user: User, token: str, request=None
    ) -> None:
        reset_url = f"{settings.frontend_url}/reset-password?token={token}"
        await send_email(
            to=user.email,
            subject="Restablecer contraseña",
            body=(
                f"Hola,\n\n"
                f"Has solicitado restablecer tu contraseña.\n\n"
                f"Abre este enlace para crear una nueva:\n"
                f"{reset_url}\n\n"
                f"El enlace caduca en 1 hora. Si no has sido tú, ignora este correo."
            ),
        )

    async def on_after_request_verify(
        self, user: User, token: str, request=None
    ) -> None:
        verify_url = f"{settings.frontend_url}/verify?token={token}"
        await send_email(
            to=user.email,
            subject="Verifica  tu correo en HostIQ",
            body=(
                f"Hola {user.nombre or 'Nuevo Usuario'} {user.apellidos or ''},\n\n"
                f"Gracias por registrarte.\n\n"
                f"Confirma tu correo para seguir el proceso de alta en HostIQ, abriendo este enlace:\n"
                f"{verify_url}\n\n"
                f"El enlace caduca en 24 horas."
            ),
        )

    async def _send_verification_email(self, user: User) -> None:
        """Genera un token de verificación y lo envía por email."""
        try:
            token = self._generate_verification_token(user)
            await self.on_after_request_verify(user, token)
        except Exception as exc:
            # Un fallo de email no debe tumbar el registro.
            print(f"[REGISTER] No se pudo enviar email de verificación a {user.email}: {exc}")

    def _generate_verification_token(self, user: User) -> str:
        """Genera manualmente un token JWT de verificación."""
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "aud": self.verification_token_audience,
        }
        return generate_jwt(
            token_data,
            self.verification_token_secret,
            self.verification_token_lifetime_seconds,
        )


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


# ---------- Authentication backend ----------

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.app_secret_key,
        lifetime_seconds=settings.jwt_lifetime_seconds,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


# ---------- FastAPIUsers ----------

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)


current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)