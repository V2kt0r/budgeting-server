from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import (
    DeclarativeBase,
    MappedAsDataclass,
    declared_attr,
    sessionmaker,
)

from ..config import settings
from ..utils.snake_case import snake_case


class Base(MappedAsDataclass, DeclarativeBase):
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return snake_case(cls.__name__)


DATABASE_URI = settings.POSTGRES_URI
DATABASE_PREFIX = settings.POSTGRES_ASYNC_PREFIX
DATABASE_URL = f"{DATABASE_PREFIX}{DATABASE_URI}"

async_engine: AsyncEngine = create_async_engine(
    DATABASE_URL, echo=False, future=True
)

local_session = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async_session = local_session
    async with async_session() as db:
        yield db
