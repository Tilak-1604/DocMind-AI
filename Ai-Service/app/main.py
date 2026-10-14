from fastapi import FastAPI

from app.core.database import Base, engine
from app.api.router import router

# Import all models so SQLAlchemy registers them before create_all
import app.models 

# Auto-create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DocMind AI RAG Engine")

app.include_router(router)