from app.core.config import settings
from app.db.database_helper import DatabaseHelper

db_helper = DatabaseHelper(
    url=str(settings.db.url),
    echo=settings.db.echo,
    echo_pool=settings.db.echo_pool,
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow,
)


async def get_session():
    async for session in db_helper._session_getter():
        yield session
