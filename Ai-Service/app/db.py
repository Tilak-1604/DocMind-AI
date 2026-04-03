from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Database connection pooling for optimal performance
# pool_size: Number of connections to maintain in the pool
# max_overflow: Additional connections when pool is exhausted
# pool_pre_ping: Verify connection health before using
# pool_recycle: Recycle connections after 1 hour to avoid stale connections
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=pool.QueuePool,
    pool_size=20,              # Base connection pool size
    max_overflow=10,           # Emergency connections
    pool_pre_ping=True,        # Test connections before use
    pool_recycle=3600,         # Recycle every hour (3600s)
    echo=False                 # Disable SQL logging in production
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()