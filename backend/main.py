"""
Enthropy FastAPI application entry point.

This module creates the FastAPI app, registers routes, and sets up
startup/shutdown lifecycle events.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import router
from backend.config.settings import get_settings

settings = get_settings()

app = FastAPI(
    title="Enthropy",
    description="A continual-learning knowledge engine",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
async def health_check() -> dict:
    """Return service health status."""
    return {"status": "ok", "service": "enthropy"}
