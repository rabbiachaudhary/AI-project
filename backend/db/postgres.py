from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import settings


def _asyncpg_url(url: str) -> tuple[str, dict]:
    """Convert postgres URL to asyncpg format, stripping params asyncpg doesn't accept."""
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            url = "postgresql+asyncpg://" + url[len(prefix):]
            break

    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    ssl_mode = params.pop("sslmode", ["disable"])[0]
    params.pop("channel_binding", None)

    clean_url = urlunparse(parsed._replace(query=urlencode({k: v[0] for k, v in params.items()})))
    connect_args = {"ssl": True} if ssl_mode in ("require", "verify-ca", "verify-full") else {}
    return clean_url, connect_args


_db_url, _connect_args = _asyncpg_url(settings.postgres_url)
_connect_args["command_timeout"] = 30
engine = create_async_engine(
    _db_url,
    connect_args=_connect_args,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db():
    async with engine.begin() as conn:
        from models.pg_models import User, Profile  # noqa: F401 — registers tables with Base
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
