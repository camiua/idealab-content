"""Ruta de generación de posts."""

import time

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.api.schemas import GenerateRequest, GenerateResponse, Metrics
from app.config import Provider, settings
from app.llm.providers import (
    get_chat_model,
    get_model_name,
    is_rate_limit_error,
    is_unavailable_error,
)
from app.services.generation import generate_post

router = APIRouter(tags=["generate"])

UNAVAILABLE_MESSAGES = {
    "ollama": "Ollama no responde. Prueba con Groq.",
    "groq": "Groq no está disponible. Revisa la clave o prueba con Ollama.",
}
RATE_LIMIT_MESSAGE = "Límite de Groq alcanzado. Prueba con Ollama o espera un momento."


def provider_error_response(exc: Exception, provider: Provider) -> JSONResponse | None:
    """Traduce un fallo del proveedor a un 503 o un 429 con mensaje claro (spec §1.3)."""
    if is_rate_limit_error(exc):
        status, detail = 429, RATE_LIMIT_MESSAGE
    elif is_unavailable_error(exc):
        status, detail = 503, UNAVAILABLE_MESSAGES[provider]
    else:
        return None
    return JSONResponse(status_code=status, content={"detail": detail, "provider": provider})


@router.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest):
    provider = request.provider or settings.default_provider
    start = time.perf_counter()

    try:
        model = get_chat_model(provider)
        result = generate_post(request.topic, request.platform, request.audience, model)
    except Exception as exc:
        error = provider_error_response(exc, provider)
        if error is None:
            raise
        return error

    return GenerateResponse(
        content=result.content,
        platform=request.platform,
        provider=provider,
        model=get_model_name(provider),
        metrics=Metrics(elapsed_ms=round((time.perf_counter() - start) * 1000)),
        warnings=result.warnings,
        prompt_versions=result.prompt_versions,
    )