# Imagen base: Python 3.12 en una versión mínima de Debian
FROM python:3.12-slim

# uv, copiado desde su imagen oficial (misma versión que en local)
COPY --from=ghcr.io/astral-sh/uv:0.11.26 /uv /uvx /bin/
WORKDIR /app

# Ajustes de uv para contenedores
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# 1) Primero solo las dependencias: Docker guarda esta capa en caché
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# 2) Después, el código de la app
COPY app ./app

EXPOSE 8000

# Render indica el puerto en la variable PORT; en local se usa 8000
CMD ["sh", "-c", "/app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]