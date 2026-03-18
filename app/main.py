from fastapi import FastAPI, APIRouter
from app.api.v1 import router as api_router
from app.core.config import settings
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from app.db.database import engine, Base
from app.models.recurrence_rule import RecurrenceRule
from app.models.task import Task

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"DATABASE_URL: {engine.url}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get('/health')
async def health():
    # check DB and Redis connectivity
    ok = {"db": False, "redis": False}
    try:
        async with engine.connect() as conn:
            await conn.execute(__import__('sqlalchemy').text('SELECT 1'))
            ok['db'] = True
    except Exception:
        ok['db'] = False
    try:
        r = await aioredis.from_url(settings.redis_url)
        await r.ping()
        ok['redis'] = True
    except Exception:
        ok['redis'] = False
    return {"status": "ok" if all(ok.values()) else "degraded", "checks": ok}
