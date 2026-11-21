import logging
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.config import settings
from app.db.database import get_session
from app.models.admin_activation_token import AdminActivationToken
from app.models.user import User, UserRole
from app.utils.url_builder import build_admin_activation_url

logger = logging.getLogger(__name__)


async def run_seed():
    """
    Проверяет наличие администратора. Если нет — создаёт одноразовый токен
    и выводит ссылку для активации первого администратора.
    """
    async for session in get_session():
        result = await session.execute(select(User).where(User.role == UserRole.ADMIN).limit(1))
        if result.scalar_one_or_none() is not None:
            logger.info("Администратор уже существует. Пропускаем генерацию токена.")
            return

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(
            minutes=settings.admin_token_expire_minutes
        )

        session.add(AdminActivationToken(token=token, expires_at=expires_at))
        await session.commit()

        activation_url = build_admin_activation_url(token)

        if settings.deploy_mode == "production":
            logger.info(
                "\n%s\n Ссылка для активации администратора:\n %s\n Срок действия: %d минут\n%s",
                "=" * 60,
                activation_url,
                settings.admin_token_expire_minutes,
                "=" * 60,
            )
        else:
            logger.info("Создан токен активации администратора: %s", token)
            logger.info("Ссылка активации: %s", activation_url)
