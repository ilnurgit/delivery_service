from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from delivery.core.settings import settings


def create_engine() -> AsyncEngine:
    return create_async_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
    )


engine: AsyncEngine = create_engine()
