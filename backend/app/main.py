"""Punto de entrada del backend de IdeaLab Content."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import generate, health
from app.config import settings

app = FastAPI(
    title="IdeaLab Content API",
    description="Generador de contenido para blogs y redes sociales con IA generativa.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(generate.router, prefix="/api")