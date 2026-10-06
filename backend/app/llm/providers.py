"""Único punto de acceso a los modelos de chat (Ollama y Groq)."""

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from app.config import Provider, settings


class ProviderNotConfiguredError(Exception):
    """El proveedor pedido no se puede usar (por ejemplo, falta su API key)."""


def get_chat_model(
    provider: Provider | None = None, temperature: float = 0.7
) -> BaseChatModel:
    """Devuelve el modelo de chat del proveedor pedido, o el de por defecto."""
    provider = provider or settings.default_provider

    if provider == "ollama":
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=temperature,
        )

    if provider == "groq":
        if settings.groq_api_key is None:
            raise ProviderNotConfiguredError("Falta GROQ_API_KEY en el archivo .env")
        return ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=temperature,
        )

    raise ValueError(f"Proveedor desconocido: {provider}")