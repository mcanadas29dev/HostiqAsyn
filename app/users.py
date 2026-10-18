import uuid
from collections.abc import AsyncGenerator

from fastapi import BackgroundTasks, Depends
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

    def __init__(
        self,
        user_db: SQLAlchemyUserDatabase,
        background_tasks: BackgroundTasks,
    ):
        super().__init__(user_db)
        self.background_tasks = background_tasks

    async def on_after_register(self, user: User, request=None) -> None:
        token = self._generate_verification_token(user)
        self.background_tasks.add_task(self._send_verification_email_task, user, token)

    async def on_after_forgot_password(
        self, user: User, token: str, request=None
    ) -> None:
        reset_url = f"{settings.frontend_url}/reset-password?token={token}"
        self.background_tasks.add_task(
            send_email,
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
        self.background_tasks.add_task(self._send_verification_email_task, user, token)

    async def _send_verification_email_task(self, user: User, token: str) -> None:
        """Tarea que se ejecuta en background para enviar el correo."""
        try:
            verify_url = f"{settings.frontend_url}/verify?token={token}"
            await send_email(
                to=user.email,
                subject="Verifica tu correo en HostIQ",
                body=(
                    f"Hola {user.nombre or 'Nuevo Usuario'} {user.apellidos or ''},\n\n"
                    f"Gracias por registrarte.\n\n"
                    f"Confirma tu correo para seguir el proceso de alta en HostIQ, "
                    f"abriendo este enlace:\n"
                    f"{verify_url}\n\n"
                    f"El enlace caduca en 24 horas."
                ),
            )
        except Exception as exc:
            print(f"[BACKGROUND EMAIL] Falló el envío a {user.email}: {exc}")

    def _generate_verification_token(self, user: User) -> str:
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
    background_tasks: BackgroundTasks,
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db, background_tasks)


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