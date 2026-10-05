"""Punto de entrada del backend de IdeaLab Content."""

from fastapi import FastAPI

from app.api.routes import health

app = FastAPI(
    title="IdeaLab Content API",
    description="Generador de contenido para blogs y redes sociales con IA generativa.",
    version="0.1.0",
)

app.include_router(health.router, prefix="/api")