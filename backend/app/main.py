from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.db.session import Base, engine
from app.models import entities  # noqa: F401
from app.services.files import ensure_storage_dirs

settings = get_settings()

app = FastAPI(title="MANDRONG API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_web_origins,
    allow_origin_regex=settings.web_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    ensure_storage_dirs()
    if settings.database_url.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(router)
