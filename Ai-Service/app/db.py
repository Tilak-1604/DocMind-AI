# Backward-compatibility shim.
# All new code should import from app.core.database directly.
from app.core.database import engine, SessionLocal, Base, get_db  # noqa: F401