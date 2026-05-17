import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parents[1]


def run_migrations() -> None:
    alembic_cfg = Config(str(BASE_DIR / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(BASE_DIR / "alembic"))
    command.upgrade(alembic_cfg, "head")


async def run_migrations_with_retry() -> None:
    for attempt in range(1, 11):
        try:
            await asyncio.to_thread(run_migrations)
            return
        except Exception:
            if attempt == 10:
                raise

            logger.warning("Database migration failed; retrying in 2 seconds", exc_info=True)
            await asyncio.sleep(2)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await run_migrations_with_retry()
    app.state.settings = settings
    yield


app = FastAPI(title="University Equipment Rental System", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
