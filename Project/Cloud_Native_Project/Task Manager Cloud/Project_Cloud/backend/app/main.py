from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import time

from app.core.database import engine, Base
from app.api import tasks, health

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — connecting to DB...")
    Base.metadata.create_all(bind=engine)
    logger.info("DB tables ready.")
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="DevOps Task Manager API",
    version="1.0.0",
    description="Production-grade task manager — EKS + RDS + ALB",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod via env var
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
