# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Determine the DB URL — fall back to SQLite if PostgreSQL is not configured
_raw_url = settings.DATABASE_URL or ""
_is_placeholder = ("user:password" in _raw_url or not _raw_url)

if _is_placeholder:
    DATABASE_URL = "sqlite+aiosqlite:///./wa_bot.db"
    print("[WARNING] Using SQLite (local dev). Set DATABASE_URL in .env for PostgreSQL.")
elif _raw_url.startswith("postgresql://"):
    DATABASE_URL = _raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    DATABASE_URL = _raw_url

engine = create_async_engine(DATABASE_URL, echo=settings.DEBUG)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    """FastAPI dependency to get an async DB session."""
    async with async_session() as session:
        yield session

async def init_db():
    """Create all tables on startup."""
    async with engine.begin() as conn:
        from app.models import tenant, customer, analytics, knowledge  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
