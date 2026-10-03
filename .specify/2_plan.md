# 2. Plan — organización y ejecución

Repo: **`idealab-content`** · rama de trabajo: `develop` · rama estable: `main`

---

## 2.1 Principios de trabajo

- **Entender antes de implementar.** Cada tarea empieza identificando los conceptos que implica
  (patrones, librerías, técnicas de PLN). Se implementa cuando están claros.
- **Incrementos pequeños y verificables.** Una tarea, una rama, un PR. Cada tarea termina con un
  criterio de "hecho" que se puede comprobar.
- **Las decisiones se documentan con su motivo.** Si una elección no se puede justificar, no se toma.
- **Los prompts se mejoran midiendo**, no a ojo: cada versión pasa por el banco de pruebas.
- **La complejidad entra cuando un nivel la necesita**, no antes.
- **Lo aprendido se anota al momento** en la sección *Aprendizajes* de `docs/decisiones.md`.

---

## 2.2 Stack

| Capa | Tecnología |
|---|---|
| Frontend | React · Vite · JavaScript · Tailwind CSS 4 · react-markdown |
| Backend | Python · FastAPI · Pydantic · uv |
| IA | LangChain · LangSmith · LangGraph |
| Modelos | Llama 3.2 (Ollama, local) · Llama en Groq (nube) |
| RAG | arXiv · Chroma · embeddings multilingües locales · NetworkX (Graph RAG) |
| Integraciones | Unsplash (imágenes) · yfinance (mercados) |
| Calidad | pytest · ruff · pre-commit · gitleaks · GitHub Actions |
| Entorno | Docker · Docker Compose · Git y GitHub |
| Gestión | GitHub Issues · GitHub Projects |

Las versiones exactas quedan fijadas en `backend/uv.lock` y `frontend/package-lock.json`.

---

## 2.3 Estructura del repositorio

Estructura **final**. Las carpetas marcadas con nivel se crean al llegar a ese nivel, no antes.

```
idealab-content/
├── .specify/                     ← 1_spec.md, 2_plan.md, 3_tasks.md
├── .github/
│   ├── ISSUE_TEMPLATE/tarea.md
│   ├── pull_request_template.md
│   └── workflows/ci.yml          (🟡)
├── backend/
│   ├── app/
│   │   ├── main.py               ← crea la app y registra las rutas
│   │   ├── config.py             ← lee el .env (pydantic-settings)
│   │   ├── api/
│   │   │   ├── routes/           ← un archivo por funcionalidad
│   │   │   └── schemas.py        ← contratos de entrada y salida
│   │   ├── services/             ← casos de uso: generate, refine, finance, science
│   │   ├── llm/providers.py      ← ÚNICO punto de acceso a Ollama y Groq
│   │   ├── prompts/
│   │   │   ├── templates/        ← ver spec §1.5
│   │   │   └── builder.py
│   │   ├── integrations/         ← images.py (🟡), markets.py (🟠)
│   │   ├── rag/                  (🟠)
│   │   ├── guardrails/           (🔴)
│   │   └── agents/               (🔴)
│   ├── scripts/
│   │   ├── spike_first_post.py
│   │   ├── eval_prompts.py       ← banco de pruebas de prompts
│   │   └── ingest_arxiv.py       (🟠)
│   ├── tests/
│   ├── data/                     ← índice de Chroma y grafo (no se sube)
│   ├── pyproject.toml
│   ├── uv.lock
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/client.js         ← ÚNICO punto de llamada al backend
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── data/profiles.js      ← perfiles de empresa de ejemplo
│   │   ├── index.css             ← Tailwind y variante de modo oscuro
│   │   └── App.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docs/
│   ├── arquitectura.png
│   ├── decisiones.md             ← decisiones ampliadas y Aprendizajes
│   └── prompt-engineering.md     ← evolución de los prompts y resultados
├── scripts/setup_github.sh       ← crea labels, milestones e issues
├── .pre-commit-config.yaml
├── docker-compose.yml            ← en la raíz
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## 2.4 Reglas del backend

1. **Capas:** las rutas llaman a servicios; los servicios llaman a `llm/`, `prompts/`, `integrations/` y `rag/`. Nunca al revés.
2. **Rutas finas:** reciben, validan, llaman a un servicio y responden. Sin lógica de negocio.
3. **Los servicios no saben de HTTP.** No importan nada de FastAPI. Así los reutilizan los agentes y los tests.
4. **Solo `llm/providers.py` importa** `langchain_ollama` y `langchain_groq`.
5. **Ningún prompt escrito dentro del código Python.** Todos en `prompts/templates/`.
6. **Ningún valor de configuración fijo en el código.** Todo pasa por `config.py`.
7. **Errores controlados:** los fallos de proveedor se traducen a 503 o 429 con mensaje claro (spec §1.3).
8. **Type hints** en todas las funciones públicas.

## 2.5 Reglas del frontend

1. **Toda llamada al backend pasa por `src/api/client.js`.** Ningún `fetch` suelto en los componentes.
2. **Tailwind CSS 4** con el plugin `@tailwindcss/vite`. Sin `tailwind.config.js` ni PostCSS. Si un recurso explica la versión 3, no se sigue.
3. **Mobile first:** se diseña para móvil y se amplía con `md:` y `lg:`.
4. **Modo oscuro** con variante por clase (`dark:`), activable con un botón y respetando la preferencia del sistema al entrar.
5. **Componentes pequeños**, uno por archivo.
6. **Estados visibles:** cargando, error y vacío en toda acción que llame al backend.
7. **Accesibilidad básica:** `alt` en las imágenes, `label` en los campos y contraste suficiente en los dos temas.

---

## 2.6 Docker

| Servicio | Imagen | Puerto |
|---|---|---|
| `backend` | Python con `uv`, `uvicorn` | 8000 |
| `frontend` | Build de Vite servido por `nginx:alpine` | 5173 → 80 |

- `docker-compose.yml` en la raíz. Lee las variables de `.env`.
- **Ollama no va en Docker.** El backend lo alcanza en `http://host.docker.internal:11434`
  (con `extra_hosts: host.docker.internal:host-gateway` para que funcione también en Linux).
- `backend/data/` se monta como volumen para conservar el índice del RAG.
- Objetivo: con una clave de Groq en `.env`, `docker compose up` basta para usar la aplicación.

---

## 2.7 Ramas, commits y PRs

- `main`: solo recibe merges desde `develop` al cerrar cada nivel. Siempre funciona.
- `develop`: integración. Rama por defecto. Nunca se trabaja directamente en ella.
- Ramas de trabajo, **una por tarea**, en inglés:
  - `feature/<área>-<descripción>` → `feature/backend-prompt-templates`
  - `fix/<área>-<descripción>` → `fix/api-x-length-limit`
  - `docs/<descripción>` → `docs/readme-setup`
- `main` y `develop` están protegidas: sin borrado, sin *force push* y solo mediante PR.
- **Commits convencionales.** Prefijo en inglés y mensaje en español:
  - `feat(prompts): plantilla de instagram v2 con gancho inicial`
  - `fix(api): limitar los posts de X a 280 caracteres`
  - Prefijos: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`.
- **Cada PR** usa la plantilla y cierra su issue: `Closes #12`.
- **Método de merge:** siempre *Create a merge commit*.
- **Tags** al cerrar cada nivel: `v1-esencial`, `v2-medio`, `v3-avanzado`, `v4-experto` y `v1.0` en la entrega.

**Idiomas:** código, nombres de archivos y ramas en inglés. Commits, issues, PRs, documentación e interfaz en español.

---

## 2.8 Issues, labels, milestones y tablero

- **Una issue por tarea** de `3_tasks.md`, titulada con su ID: `T-1.4 · Plantillas de prompt v1`.
- La issue no repite el diseño: enlaza a la sección de la spec. Si la issue y la spec no coinciden, manda la spec.
- **Labels:** `nivel:esencial|medio|avanzado|experto|mejora|soporte|seguridad`, `área:backend|frontend|ia|docs|infra`, `gate`.
- **Milestones:** uno por nivel más `Entrega`.
- **Tablero (GitHub Projects):** `Backlog` · `Por hacer` · `En curso` · `En revisión` · `Hecho`.
- Labels, milestones e issues se crean con `scripts/setup_github.sh`, que lee `3_tasks.md`. Así las issues no pueden desincronizarse de las tareas.

---

## 2.9 Calidad

- **Tests (pytest):** usan un **modelo falso de LangChain**, sin red ni Ollama. Rápidos, gratuitos y deterministas.
- **Linter (ruff)** en el backend.
- **pre-commit con gitleaks:** bloquea cualquier commit que contenga un secreto.
- **CI (GitHub Actions)** en cada PR: `ruff` + `pytest` en el backend y `npm run build` en el frontend. Insignia en el README.
- **Banco de pruebas de prompts** (`scripts/eval_prompts.py`): temas fijos × plataformas, mismo proveedor y temperatura. Comprueba longitud, hashtags e idioma y genera una tabla comparable entre versiones.

---

## 2.10 Documentación

Se escribe **al cerrar cada nivel**, no al final.

| Documento | Contenido |
|---|---|
| `README.md` | Qué es, captura o GIF, diagrama, cómo arrancarlo (Docker y Ollama opcional), stack, estructura, herramientas de desarrollo, próximos pasos |
| `docs/decisiones.md` | Decisiones ampliadas y sección **Aprendizajes** |
| `docs/prompt-engineering.md` | Evolución de cada plantilla (v1 → vN) con los resultados del banco de pruebas |
| Artículo en Medium | Se redacta por partes: una sección por nivel |

---

## 2.11 Definición de "hecho" (válida para toda tarea)

- Cumple el criterio "Hecho" de la tarea.
- Funciona en local.
- Sin secretos en el código.
- Tests y linter en verde (desde que exista el CI).
- PR fusionado en `develop` e issue cerrada.
- Documentación o aprendizajes actualizados si la tarea lo requería.
