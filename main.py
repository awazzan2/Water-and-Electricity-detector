import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

from database import engine
import electricity, water
from RecieveElecWater import router as receive_router
from scheduler import init_sensor_states, start_scheduler, stop_scheduler
from sse_manager import sse_manager

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent


def run_migrations() -> None:
    try:
        logger.info("Starting migrations...")
        # Convert async database URL to sync for alembic
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://user:password@localhost:5432/monitor_db",
        )
        # Replace the full asyncpg dialect with just postgresql
        sync_database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
        
        alembic_cfg = Config(str(BASE_DIR / "alembic.ini"))
        alembic_cfg.set_main_option("sqlalchemy.url", sync_database_url)
        alembic_cfg.set_main_option("script_location", str(BASE_DIR / "migrations"))
        logger.info(f"Using database: {sync_database_url}")
        logger.info("Alembic config loaded, running upgrade...")
        command.upgrade(alembic_cfg, "head")
        logger.info("Alembic migrations applied")
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Skip migrations on startup - they can be run manually
    logger.warning("Skipping automatic migrations on startup. Run migrations manually if needed.")
    
    init_sensor_states()
    start_scheduler()
    logger.info("Application startup complete")
    yield
    stop_scheduler()
    await engine.dispose()


app = FastAPI(title="Water & Electricity Monitor", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(water.router, prefix="/water", tags=["water"])
app.include_router(electricity.router, prefix="/electricity", tags=["electricity"])
app.include_router(receive_router, tags=["device"])


@app.get("/events")
async def events(request: Request):
    queue = sse_manager.register()

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield {"event": "message", "data": data}
                except asyncio.TimeoutError:
                    yield {"event": "ping", "data": ""}
        finally:
            sse_manager.unregister(queue)

    return EventSourceResponse(event_generator())


frontend_dir = BASE_DIR
if frontend_dir.exists():
    app.mount(
        "/",
        StaticFiles(directory=str(frontend_dir), html=True),
        name="frontend",
    )
