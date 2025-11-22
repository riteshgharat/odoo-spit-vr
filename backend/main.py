from fastapi import FastAPI

from app.core.config import settings
from app.api.api_v1 import api_router
from app.db.session import engine
from app.db.base import Base


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(api_router, prefix=settings.API_V1_STR)
