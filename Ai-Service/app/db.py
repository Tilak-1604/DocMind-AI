from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

_db_url = settings.DATABASE_URL or ""

# SQLite (e.g. in tests) uses SingletonThreadPool which does not accept
# pool_size / max_overflow.  Apply production pool settings only for
# server-based dialects (MySQL, PostgreSQL, …).
_pool_kwargs: dict = {}
if not _db_url.startswith("sqlite"):
    _pool_kwargs = {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }

engine = create_engine(_db_url, **_pool_kwargs)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()