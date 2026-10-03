# 3. Tasks

Cada tarea se convierte en una issue de GitHub con el mismo ID en el título.
**Hecho** = criterio verificable, no "creo que funciona".
**Conceptos** = lo que hay que tener claro antes de implementar la tarea.

Leyenda: 🟢 Esencial · 🟡 Medio · 🟠 Avanzado · 🔴 Experto · ⭐ Mejora de producto · 🔐 Seguridad · ⚪ Soporte

---

## Fase 0 — Arranque (sáb 3)

**T-0.1 · Repositorio, ramas y protección** ⚪
Repo público con README, `.gitignore` de Python y licencia MIT. Rama `develop` por defecto. Ruleset
sobre `main` y `develop`: sin borrado, sin *force push* y PR obligatorio sin aprobaciones.
*Conceptos:* ramas, rama por defecto, protección de ramas.
*Hecho:* `git branch -a` muestra `main` y `develop` en remoto, y `develop` es la rama por defecto.

**T-0.2 · Specs iniciales** ⚪ · dep: T-0.1
`.specify/` con `1_spec.md`, `2_plan.md` y `3_tasks.md`.
*Conceptos:* desarrollo guiado por especificaciones, flujo rama → PR → merge.
*Hecho:* primer PR fusionado en `develop` con las tres specs.

**T-0.3 · Estructura base y configuración** ⚪ · dep: T-0.2
Carpetas `backend/`, `frontend/`, `docs/` y `scripts/`. `.gitignore` ampliado (Python, Node, `.env`,
`.venv`, `node_modules`, `backend/data/`). `.env.example` con las variables de la spec §1.6. README
mínimo con el objetivo y el diagrama en `docs/arquitectura.png`.
*Conceptos:* `.gitignore`, variables de entorno, secretos.
*Hecho:* `git status` no muestra nunca `.env` aunque exista.

**T-0.4 · Detector de secretos** 🔐 · dep: T-0.3
`pre-commit` con el hook de `gitleaks`.
*Conceptos:* hooks de Git, pre-commit.
*Hecho:* un commit con una clave falsa de prueba queda bloqueado.

**T-0.5 · Plantillas de issue y PR** ⚪ · dep: T-0.3
`.github/ISSUE_TEMPLATE/tarea.md` y `.github/pull_request_template.md`.
*Hecho:* al crear una issue o un PR en GitHub, aparece la plantilla.

**T-0.6 · Labels, milestones, issues y tablero** ⚪ · dep: T-0.5
`scripts/setup_github.sh` con GitHub CLI: crea labels y milestones (plan §2.8) y una issue por
tarea leyendo este archivo. Tablero en GitHub Projects con cinco columnas.
*Conceptos:* scripts de bash, GitHub CLI.
*Hecho:* todas las tareas tienen su issue, con label y milestone, y aparecen en el tablero.

**T-0.7 · Entorno local** ⚪
`uv`, Node LTS, Docker Desktop, Ollama con `llama3.2` y cuenta de Groq con API key en `.env`.
*Hecho:* `ollama run llama3.2` responde y la clave de Groq está en `.env` (no en Git).

---

## Fase 1 — Nivel Esencial (sáb 3 – lun 5)

**T-1.1 · Spike: primer post con LangChain** 🟢 · dep: T-0.7
`backend/scripts/spike_first_post.py`: el mismo prompt enviado a Ollama y a Groq, imprimiendo
respuesta y tiempo. Se anotan los tiempos en *Aprendizajes*.
*Conceptos:* LLM, `invoke`, mensajes de sistema y de usuario, temperatura.
*Hecho:* el script genera un post con cada proveedor y los tiempos están anotados.

**T-1.2 · Proyecto backend y configuración** 🟢 · dep: T-1.1
`uv init`, FastAPI, `config.py` con pydantic-settings, `GET /api/health` básico.
*Conceptos:* API REST, FastAPI, pydantic-settings.
*Hecho:* `uv run uvicorn app.main:app --reload` arranca y `/api/health` responde.

**T-1.3 · Punto único de acceso al LLM** 🟢 · dep: T-1.2
`llm/providers.py` con `get_chat_model(provider, temperature)`.
*Conceptos:* patrón Factory, interfaz común de LangChain para modelos de chat.
*Hecho:* el mismo código funciona con `ollama` y con `groq`, y ningún otro módulo importa sus librerías.

**T-1.4 · Plantillas de prompt v1** 🟢 · dep: T-1.3
`prompts/templates/` (spec §1.5) y `prompts/builder.py`. Reglas de §1.4.
*Conceptos:* system prompt, plantillas con variables, restricciones, few-shot.
*Hecho:* el builder genera el prompt completo para cualquier combinación de plataforma y audiencia.

**T-1.5 · Servicio de generación y comprobación de reglas** 🟢 · dep: T-1.4
`services/generation.py`: construye el prompt, llama al modelo y comprueba longitud y hashtags.
Si falla, regenera una vez; si vuelve a fallar, devuelve un aviso.
*Conceptos:* capa de servicios, validación posterior a la generación.
*Hecho:* un post de X nunca se devuelve con más de 280 caracteres sin aviso.

**T-1.6 · API de generación** 🟢 · dep: T-1.5
`POST /api/generate`, `schemas.py`, CORS y errores 503 y 429 (spec §1.3).
*Conceptos:* Pydantic, CORS, códigos de estado HTTP.
*Hecho:* desde `/docs` se genera un post; con Ollama apagado se recibe un 503 con mensaje claro.

**T-1.7 · Tests del backend** 🟢 · dep: T-1.6
pytest con un modelo falso de LangChain para el builder, el servicio y la ruta.
*Conceptos:* tests unitarios, *mocks*, inyección de dependencias en FastAPI.
*Hecho:* `uv run pytest` pasa sin red y sin Ollama.

**T-1.8 · Banco de pruebas y registro de prompts** 🟢 · dep: T-1.5
`scripts/eval_prompts.py`: cinco temas fijos × cuatro plataformas. Tabla con el porcentaje de
cumplimiento de reglas. `docs/prompt-engineering.md` con v1 y una primera mejora (v2).
*Conceptos:* evaluación de prompts, condiciones comparables.
*Hecho:* la tabla v1 vs v2 está en `docs/prompt-engineering.md`.

**T-1.9 · Proyecto frontend** 🟢 · dep: T-1.6
Vite + React + Tailwind 4, variante de modo oscuro, botón de tema y `src/api/client.js`.
*Conceptos:* componentes, Vite, Tailwind 4, variantes `md:` y `dark:`.
*Hecho:* `npm run dev` muestra la página y el cambio de tema funciona.

**T-1.10 · Formulario y resultado** 🟢 · dep: T-1.9
`GeneratorForm` y `PostResult` (Markdown, botón de copiar), con estados de carga y de error. Mobile first.
*Conceptos:* `useState`, peticiones asíncronas, diseño responsive.
*Hecho:* se genera un post desde la web y, en vista móvil, todo se ve en una columna.

**T-1.11 · Documentación del nivel** 🟢 · dep: T-1.10
README (cómo arrancar sin Docker) y primera sección del artículo de Medium (problema y arquitectura).
*Hecho:* alguien que no conoce el proyecto puede arrancarlo siguiendo el README.

**T-1.GATE · Nivel Esencial de punta a punta** 🟢 · dep: T-1.1 a T-1.11
*Hecho:* PR `develop` → `main` fusionado y tag `v1-esencial`.

---

## Fase 2 — Nivel Medio (mar 6)

**T-2.1 · Selector de modelo y estado de proveedores** 🟡
`/api/health` comprueba Ollama y la clave de Groq. Desplegable en la interfaz que desactiva el proveedor no disponible.
*Conceptos:* *health checks*, degradación controlada.
*Hecho:* con Ollama apagado, la opción aparece desactivada y explica por qué.

**T-2.2 · Perfil de empresa y perfiles de ejemplo** 🟡
Campo de perfil inyectado en el system prompt. Tres perfiles ficticios en `src/data/profiles.js`, seleccionables con un clic.
*Conceptos:* personalización mediante contexto en el prompt.
*Hecho:* el mismo tema genera posts con un tono claramente distinto según el perfil.

**T-2.3 · Imágenes integradas** 🟡
El LLM extrae palabras clave y texto alternativo (temperatura 0). `integrations/images.py` busca en
Unsplash. Se muestra el crédito del autor. En `blog`, la imagen va dentro del Markdown.
*Conceptos:* extracción de palabras clave, APIs externas, salida estructurada.
*Hecho:* el post incluye una imagen relacionada con su crédito; sin clave de Unsplash, la app funciona sin imagen y avisa.

**T-2.4 · Métricas en pantalla** ⭐
Tiempo de respuesta y tokens de entrada y salida debajo de cada post.
*Hecho:* se ve, por ejemplo, "Groq · 1,8 s · 742 tokens".

**T-2.5 · Docker** 🟡
Dockerfiles de backend (con uv) y frontend (build + nginx). `docker-compose.yml` en la raíz. Ollama fuera (plan §2.6).
*Conceptos:* imagen, contenedor, compose, redes de Docker, `host.docker.internal`.
*Hecho:* desde un clon limpio, con solo la clave de Groq, `docker compose up` deja la app funcionando.

**T-2.6 · Integración continua** ⭐
GitHub Actions: `ruff`, `pytest` y `npm run build` en cada PR. Insignia en el README.
*Conceptos:* CI, *workflows* de GitHub Actions.
*Hecho:* un PR muestra las comprobaciones en verde.

**T-2.GATE · Nivel Medio** 🟡
*Hecho:* PR `develop` → `main`, tag `v2-medio` y sección del nivel Medio en el borrador de Medium.

---

## Fase 3 — Nivel Avanzado (mié 7 – jue 8)

**T-3.1 · Trazabilidad con LangSmith** 🟠 · mié 7
Variables de entorno de LangSmith. Captura de una traza para el README.
*Conceptos:* observabilidad, trazas.
*Hecho:* cada generación aparece en LangSmith con su prompt, respuesta, tiempo y tokens.

**T-3.2 · Chat de retoques** ⭐ · mié 7
`POST /api/refine` y componente `RefineChat` con botones rápidos ("Más corto", "Más formal", "Sin emojis") y campo libre.
*Conceptos:* contexto conversacional, reutilización de servicios.
*Hecho:* se pueden aplicar varios retoques seguidos sobre el mismo post.

**T-3.3 · Cuatro idiomas** 🟠 · mié 7
Parámetro `language` (ES, EN, FR, IT) en prompts e interfaz. Comprobación de idioma en el banco de pruebas.
*Conceptos:* generación multilingüe, detección de idioma.
*Hecho:* el banco de pruebas confirma el idioma correcto en los cuatro.

**T-3.4 · Noticias financieras** 🟠 · mié 7
`integrations/markets.py` con yfinance, `services/finance.py` y `POST /api/finance`. Sin
recomendaciones de inversión y con la fecha del dato.
*Conceptos:* *grounding* con datos externos, resumen de datos.
*Hecho:* el post muestra los valores reales del día, que coinciden con `market_data`.

**T-3.5 · Ingesta de arXiv en Chroma** 🟠 · mié 7
`scripts/ingest_arxiv.py` según spec §1.7. Confirmar área científica y modelo de embeddings.
*Conceptos:* chunking, embeddings, base de datos vectorial, idempotencia.
*Hecho:* ejecutarlo dos veces no duplica documentos, y una consulta de prueba devuelve fragmentos relevantes.

**T-3.6 · Artículo científico con RAG** 🟠 · jue 8
`rag/retriever.py`, `services/science.py` y `POST /api/science`. Pestaña "Ciencia" en la interfaz con las fuentes enlazadas.
*Conceptos:* RAG, búsqueda semántica, citación de fuentes.
*Hecho:* el artículo cita al menos dos papers del índice, y una pregunta fuera del área devuelve "no hay información suficiente".

**T-3.GATE · Nivel Avanzado** 🟠 · jue 8
*Hecho:* PR `develop` → `main`, tag `v3-avanzado` y sección del nivel Avanzado en el borrador de Medium.

---

## Fase 4 — Nivel Experto (jue 8 – sáb 10, 14:00)

**T-4.1 · Guardarraíles** 🔴 · jue 8
`guardrails/rules.py` y `guardrails/judge.py` (spec §1.8), aplicados a todos los servicios. Checklist visible en la interfaz. Banco de pruebas completo.
*Conceptos:* clasificación de texto, LLM como juez, detección de alucinaciones.
*Hecho:* un contenido que incumple una regla se regenera o se marca, y la interfaz lo muestra.

**T-4.2 · Sistema multiagente** 🔴 · vie 9
`agents/graph.py` con LangGraph: router → agente → guardarraíles → reintento. `POST /api/assistant`. Pestaña "Asistente" con petición libre.
*Conceptos:* agentes, grafos de estado, enrutamiento.
*Hecho:* tres peticiones de prueba (redes, finanzas, ciencia) llegan cada una al agente correcto.

**T-4.3 · Graph RAG** 🔴 · sáb 10 (mañana)
Extracción de tripletas, grafo NetworkX y su uso en `/api/science` (spec §1.7).
*Conceptos:* grafos de conocimiento, extracción de entidades y relaciones.
*Hecho:* la comparación de una misma pregunta con y sin grafo está en `docs/decisiones.md`.

**T-4.GATE · Nivel Experto y código congelado** 🔴 · sáb 10, 14:00
*Hecho:* PR `develop` → `main` y tag `v4-experto`. A partir de aquí solo se corrigen errores.

---

## Fase 5 — Entrega y exposición (sáb 10 – mié 14)

**T-5.1 · README final** · sáb 10
Captura o GIF, diagrama, instalación con Docker y Ollama opcional, stack, estructura, herramientas de desarrollo y próximos pasos.

**T-5.2 · Decisiones y aprendizajes** · sáb 10
`docs/decisiones.md` completo y diagrama actualizado.

**T-5.3 · Artículo en Medium** · dom 11 (mañana)
Unir las secciones de cada nivel, revisar y publicar.

**T-5.4 · Cierre del repositorio** · dom 11 (mañana)
Tablero sin tareas en curso, `main` actualizada y tag `v1.0`.

**Colchón** · dom 11 (tarde)
Sin nada planificado, a propósito: absorbe cualquier imprevisto de los días anteriores. Si no hace
falta, se dedica a pulir la presentación.

**T-5.5 · Entrega** · lun 12

**T-5.6 · Presentación técnica** · mar 13
Problema → arquitectura → demo → prompt engineering (v1 → vN con el banco de pruebas) → RAG y agentes → decisiones → aprendizajes → próximos pasos.

**T-5.7 · Ensayo y plan B** · mar 13
Dos ensayos cronometrados. Vídeo de la demo grabado. Ollama con el modelo precargado.
Perfiles de ejemplo listos. Adaptador de vídeo y cargador comprobados.

**T-5.8 · Exposición** · mié 14

---

## Extras (después de la entrega, o antes si hay margen)

**E-1 · Streaming de respuestas** ⭐ — el texto aparece a medida que se genera.
**E-2 · WebMCP** ⭐ — las funciones de la API, expuestas como herramientas para asistentes de IA del navegador.
**E-3 · Imagen generada con IA** ⭐ — alternativa a Unsplash con un modelo de Hugging Face.
**E-4 · Lectura en voz alta** ⭐ — botón para escuchar el post.
**E-5 · Historial de posts** ⭐ — últimos posts generados, guardados en el navegador.

---

## Calendario

| Día | Trabajo | Cierre |
|---|---|---|
| sáb 3 | Fase 0 completa · T-1.1 | |
| dom 4 | T-1.2 a T-1.8 (backend) | |
| lun 5 | T-1.9 a T-1.11 (frontend y documentación) | `v1-esencial` |
| mar 6 | Fase 2 | `v2-medio` |
| mié 7 | T-3.1 a T-3.5 | |
| jue 8 | T-3.6 · T-4.1 | `v3-avanzado` |
| vie 9 | T-4.2 | |
| sáb 10 | T-4.3 · **código congelado a las 14:00** · T-5.1 y T-5.2 | `v4-experto` |
| dom 11 | Mañana: T-5.3 · T-5.4 · **Tarde: colchón, sin planificar** | `v1.0` |
| lun 12 | **Entrega** | |
| mar 13 | Presentación, ensayo y plan B | |
| mié 14 | **Exposición** | |

## Plan de recorte

Si hay retraso, se recorta en este orden:

1. Extras pendientes.
2. T-2.4 (métricas en pantalla).
3. T-4.3 simplificado: grafo construido solo a partir de los resúmenes de los papers.
4. T-4.2 con dos agentes en lugar de tres.

**No se recortan:** los gates, el RAG científico (T-3.5 y T-3.6), el código congelado, el banco de
pruebas de prompts, el colchón del domingo ni el martes de ensayo.

Al congelar el código no entra ninguna funcionalidad nueva. Lo que no esté terminado el sábado a
las 14:00 se presenta sin ello.
