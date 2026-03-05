"""Hub FastAPI application entry point."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine
from models import Base
from routers import artifacts, config, repos, runs, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AI Agent Framework Hub",
    description="PoC Hub – orchestrates multi-agent coding runs",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(runs.router)
app.include_router(tasks.router)
app.include_router(artifacts.router)
app.include_router(config.router)
app.include_router(repos.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "hub"}
