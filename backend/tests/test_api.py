"""Tests de la API: el modelo real se sustituye por uno falso (monkeypatch)."""

from fastapi.testclient import TestClient
from langchain_core.language_models import FakeListChatModel

from app.api.routes import generate as generate_route
from app.main import app

client = TestClient(app)
VALID_X = "El café de especialidad cuida cada paso, del grano a la taza. #Café"


def test_health():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_generate_returns_a_post(monkeypatch):
    fake_model = FakeListChatModel(responses=[VALID_X])
    monkeypatch.setattr(generate_route, "get_chat_model", lambda provider: fake_model)

    response = client.post(
        "/api/generate",
        json={"topic": "Café de especialidad", "platform": "x", "audience": "general", "provider": "groq"},
    )

    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["content"] == VALID_X
    assert data["platform"] == "x"
    assert data["warnings"] == []


def test_generate_rejects_a_too_short_topic():
    response = client.post("/api/generate", json={"topic": "a", "platform": "x"})

    assert response.status_code == 422


def test_generate_returns_503_when_the_provider_is_down(monkeypatch):
    def unavailable(provider):
        raise ConnectionError("Ollama apagado")

    monkeypatch.setattr(generate_route, "get_chat_model", unavailable)

    response = client.post(
        "/api/generate",
        json={"topic": "Café de especialidad", "platform": "x", "audience": "general", "provider": "ollama"},
    )

    assert response.status_code == 503, response.json()
    assert response.json()["detail"] == "Ollama no responde. Prueba con Groq."