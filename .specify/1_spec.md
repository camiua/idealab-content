# 1. Spec — IdeaLab Content

> Fuente de verdad del **diseño**. Si algo de aquí cambia, se actualiza este archivo antes de tocar código.
> El progreso vive en GitHub Issues y en el tablero, no aquí.

---

## 1.1 Objetivo

**Digital Content** es una agencia que publica a diario en blogs, Instagram, LinkedIn y X, y
su equipo dedica muchas horas a redactar cada publicación. **IdeaLab Content** es una prueba
de concepto que genera contenido **listo para publicar** (texto e imagen) a partir de unos
pocos datos: tema, plataforma, audiencia e idioma.

**Restricción principal:** minimizar el gasto mientras la empresa valida el sistema. Solo se
usan modelos en local o APIs gratuitas, aceptando sus límites de velocidad y de peticiones.

**Alcance comprometido:** los cuatro niveles del briefing (Esencial, Medio, Avanzado y Experto)
más el chat de retoques.
**Código congelado:** sábado 10 de octubre, 14:00. **Entrega:** lunes 12. **Exposición:** miércoles 14 (presencial).

---

## 1.2 Decisiones de arquitectura

| # | Decisión | Motivo |
|---|---|---|
| D-1 | **Frontend en React (Vite + JavaScript + Tailwind CSS 4)**, separado del backend | Separa la interfaz de la lógica de IA, permite que la API se use desde otros clientes y facilita el diseño responsive y el modo oscuro. |
| D-2 | **Backend en Python con FastAPI y LangChain** | Python concentra el ecosistema de IA. FastAPI valida con Pydantic y genera la documentación de la API en `/docs`. |
| D-3 | **Dos proveedores de LLM: Ollama (local) y Groq (nube)**, elegibles por petición | Coste cero. Ollama no tiene límites y funciona sin internet; Groq es rápido y no depende del equipo. El equipo de desarrollo no tiene GPU dedicada, así que Groq es el proveedor por defecto en la demo. |
| D-4 | **Un único punto de acceso al LLM** (`llm/providers.py`) | Cambiar o añadir un proveedor es tocar un archivo. Ningún otro módulo importa Ollama ni Groq. |
| D-5 | **Los prompts son archivos versionados**, no texto dentro del código | Se mejoran sin tocar Python y su evolución queda en el historial de Git. Cada versión se mide (ver D-12). |
| D-6 | **Backend sin estado y sin base de datos** | El perfil de empresa viaja en cada petición. Menos piezas, menos fallos. La única persistencia es el índice del RAG. |
| D-7 | **Ingesta del RAG separada de la consulta** | Descargar, trocear y vectorizar papers se hace una vez con un script. La app solo consulta, y por eso responde rápido. |
| D-8 | **Embeddings multilingües ejecutados en local** | Los papers están en inglés y las peticiones pueden llegar en cuatro idiomas. Un modelo multilingüe hace la búsqueda semántica entre idiomas sin coste. |
| D-9 | **Imágenes desde un banco de fotos (Unsplash)**, con el autor acreditado | Gratis, rápido y fiable en la demo. La generación con IA queda como opción futura (E-3). |
| D-10 | **Guardarraíles en el backend** | En el navegador se podrían desactivar. En el backend, todo contenido pasa obligatoriamente por el control. |
| D-11 | **Dependencias con `uv` y lockfile** | El entorno local y Docker usan exactamente las mismas versiones. |
| D-12 | **Banco de pruebas de prompts** con temas fijos y comprobaciones automáticas | Convierte el prompt engineering en algo medible: cada versión se compara con la anterior en las mismas condiciones. |
| D-13 | **Docker para la aplicación (frontend y backend); Ollama queda fuera** | Ollama corre instalado en el sistema y el backend lo alcanza por `host.docker.internal`. En un contenedor y sin GPU iría aún más lento. Con Groq, la app funciona solo con `docker compose up`. |
| D-14 | **Secretos solo en `.env`**, con detector de secretos antes de cada commit | El repositorio es público. `.env.example` documenta las variables sin valores. |

---

## 1.3 Contrato A — API

Base: `http://localhost:8000`. Documentación interactiva en `/docs`. Todas las respuestas en JSON.

### Tipos comunes

| Campo | Valores |
|---|---|
| `platform` | `blog`, `instagram`, `linkedin`, `x` |
| `audience` | `general`, `profesional`, `juvenil`, `infantil` |
| `language` | `es`, `en`, `fr`, `it` (por defecto `es`) |
| `provider` | `ollama`, `groq` |

### Endpoints

| Método y ruta | Nivel | Qué hace |
|---|---|---|
| `GET /api/health` | 🟢 | Estado del servicio y disponibilidad de cada proveedor |
| `POST /api/generate` | 🟢 | Genera un post para una plataforma |
| `POST /api/refine` | ⭐ | Modifica un post existente según una instrucción |
| `POST /api/finance` | 🟠 | Genera una noticia con datos de mercado del día |
| `POST /api/science` | 🟠 | Genera un artículo divulgativo con RAG sobre arXiv |
| `POST /api/assistant` | 🔴 | Petición en lenguaje libre; un router decide qué agente la atiende |

### `GET /api/health`

```json
{ "status": "ok", "providers": { "ollama": true, "groq": false } }
```

`groq` es `false` si no hay clave configurada. `ollama` es `false` si no responde en `OLLAMA_BASE_URL`.

### `POST /api/generate`

Petición:
```json
{
  "topic": "Café de especialidad",
  "platform": "instagram",
  "audience": "juvenil",
  "language": "es",
  "provider": "groq",
  "company_profile": "Cafetería de barrio en Madrid. Tono cercano y divertido.",
  "include_image": true
}
```
- `topic`: obligatorio, 3–200 caracteres.
- `company_profile`: opcional, máximo 1.000 caracteres.

Respuesta:
```json
{
  "content": "¿Sabías que...",
  "platform": "instagram",
  "provider": "groq",
  "model": "llama-3.1-8b-instant",
  "image": {
    "url": "https://images.unsplash.com/...",
    "alt": "Taza de café sobre una mesa de madera",
    "author": "Ana López",
    "author_url": "https://unsplash.com/@...",
    "source": "unsplash"
  },
  "metrics": { "elapsed_ms": 1840, "input_tokens": 512, "output_tokens": 230 },
  "warnings": [],
  "guardrails": null
}
```
- `image` es `null` si no se pidió o si no hay clave de Unsplash (en ese caso se añade un aviso a `warnings`).
- `content` va en Markdown. En `blog`, la imagen se inserta dentro del propio Markdown.
- `guardrails` se rellena a partir del nivel Experto (§1.8).

### `POST /api/refine`

```json
{ "content": "...", "instruction": "Hazlo más corto", "platform": "x", "language": "es", "provider": "groq" }
```
Respuesta: mismo formato que `/api/generate`, sin `image`.

### `POST /api/finance`

```json
{ "ticker": "^IBEX", "platform": "x", "audience": "general", "language": "es", "provider": "groq" }
```
Respuesta: formato de `/api/generate` más `market_data`:
```json
{ "market_data": { "name": "IBEX 35", "close": 11240.5, "change_pct": 0.8, "date": "2026-10-07" } }
```

### `POST /api/science`

```json
{ "question": "¿Qué es un transformer?", "audience": "infantil", "language": "es", "provider": "groq" }
```
Respuesta: formato de `/api/generate` (con `platform: "blog"`) más `sources`:
```json
{ "sources": [ { "arxiv_id": "1706.03762", "title": "Attention Is All You Need", "url": "https://arxiv.org/abs/1706.03762" } ] }
```

### `POST /api/assistant`

```json
{ "request": "Hazme un tweet sobre cómo ha ido hoy el IBEX", "language": "es", "provider": "groq" }
```
Respuesta: formato del agente que la atiende, más `agent` (`social`, `finance` o `science`).

### Errores

| Código | Cuándo | Cuerpo |
|---|---|---|
| `422` | Datos de entrada no válidos | Formato estándar de FastAPI |
| `503` | El proveedor elegido no está disponible | `{ "detail": "Ollama no responde. Prueba con Groq.", "provider": "ollama" }` |
| `429` | Groq ha alcanzado su límite de peticiones | `{ "detail": "Límite de Groq alcanzado. Prueba con Ollama o espera un momento.", "provider": "groq" }` |

Nunca se devuelve al usuario el texto de una excepción interna.

---

## 1.4 Contrato B — Reglas por plataforma y audiencia

Las reglas se aplican en dos sitios: **en el prompt** (para que el modelo las cumpla) y **en una
comprobación posterior con código** (para detectar cuando no lo hace).

| Plataforma | Longitud | Estructura | Hashtags | Formato |
|---|---|---|---|---|
| `x` | **≤ 280 caracteres** | Una idea, directa | 1–2 | Texto plano |
| `instagram` | ≤ 2.200 caracteres (objetivo: 100–150 palabras) | Gancho en la primera línea, desarrollo breve, llamada a la acción | 3–5, al final | Emojis con moderación |
| `linkedin` | ≤ 3.000 caracteres (objetivo: 150–250 palabras) | Gancho, desarrollo, pregunta final | 3–5, al final | Tono profesional, sin abuso de emojis |
| `blog` | 500–800 palabras | Título H1, subtítulos H2, cierre | — | Markdown, con **meta descripción SEO ≤ 160 caracteres** al principio |

| Audiencia | Reglas |
|---|---|
| `general` | Lenguaje claro, sin tecnicismos innecesarios |
| `profesional` | Vocabulario del sector, datos concretos, tono experto |
| `juvenil` | Tono cercano, referencias actuales, frases cortas |
| `infantil` | Frases muy cortas, comparaciones con la vida diaria, sin jerga, sin contenido inapropiado |

Si una comprobación falla (por ejemplo, un post de X con más de 280 caracteres), se **regenera
una vez** indicando el error. Si vuelve a fallar, se devuelve con un aviso en `warnings`.

---

## 1.5 Contrato C — Prompts

```
backend/app/prompts/templates/
├── system.md          ← rol, idioma, reglas comunes y perfil de empresa
├── platforms/
│   ├── x.md
│   ├── instagram.md
│   ├── linkedin.md
│   └── blog.md
├── audiences.md       ← un bloque por audiencia
├── refine.md          ← instrucciones del chat de retoques
├── finance.md
├── science.md
└── judge.md           ← LLM juez de los guardarraíles
```

- Variables con llaves: `{topic}`, `{audience_rules}`, `{language}`, `{company_profile}`.
- Cada plantilla empieza con su versión en un comentario: `<!-- version: v3 -->`.
- Si no hay `company_profile`, el bloque correspondiente no se incluye en el prompt.
- **Temperatura:** 0,7 para generar contenido; 0 para extracción, router y juez.
- Cada cambio de versión se registra en `docs/prompt-engineering.md`: qué cambió, por qué y el resultado del banco de pruebas.

---

## 1.6 Contrato D — Configuración (`.env`)

| Variable | Ejemplo | Nivel |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` (en Docker: `http://host.docker.internal:11434`) | 🟢 |
| `OLLAMA_MODEL` | `llama3.2` | 🟢 |
| `GROQ_API_KEY` | *(secreto)* | 🟢 |
| `GROQ_MODEL` | Modelo Llama disponible en Groq, p. ej. `llama-3.1-8b-instant` (comprobar en la consola de Groq) | 🟢 |
| `DEFAULT_PROVIDER` | `groq` | 🟢 |
| `CORS_ORIGINS` | `http://localhost:5173` | 🟢 |
| `UNSPLASH_ACCESS_KEY` | *(secreto)* | 🟡 |
| `LANGSMITH_TRACING` | `true` | 🟠 |
| `LANGSMITH_API_KEY` | *(secreto)* | 🟠 |
| `LANGSMITH_PROJECT` | `idealab-content` | 🟠 |
| `CHROMA_PATH` | `./data/chroma` | 🟠 |

La aplicación arranca aunque falten las claves opcionales: la funcionalidad afectada se desactiva y se informa en `/api/health` o en `warnings`.

---

## 1.7 Contrato E — RAG científico y Graph RAG

**Área científica:** inteligencia artificial *(confirmar al empezar T-3.5)*.

### Ingesta (`scripts/ingest_arxiv.py`, se ejecuta una vez)

1. Busca en arXiv por el área elegida y descarga **20–30 papers**.
2. Extrae el texto y lo divide en **chunks de ~1.000 caracteres con 150 de solapamiento**.
3. Calcula los embeddings con un **modelo multilingüe local** (p. ej. `paraphrase-multilingual-MiniLM-L12-v2`). Antes de fijarlo, valorar el peso que añade a la imagen Docker.
4. Guarda los chunks en **Chroma**, en `CHROMA_PATH`, con metadatos: `arxiv_id`, `title`, `url`.
5. Es **idempotente**: si se ejecuta dos veces, no duplica documentos.

`data/` no se sube al repositorio. El README explica cómo regenerarlo.

### Consulta (`/api/science`)

1. Recupera los **4 chunks** más similares a la pregunta.
2. El prompt indica responder **solo con ese contexto** y citar las fuentes.
3. Si no hay chunks suficientemente relevantes, se responde que no hay información suficiente, en lugar de inventar.

### Graph RAG (nivel Experto)

1. **En la ingesta:** un LLM (temperatura 0) extrae de un subconjunto de chunks tripletas `(entidad, relación, entidad)`, por ejemplo `(Transformer, usa, mecanismo de atención)`. Se guardan en un grafo **NetworkX** persistido en `data/`.
2. **En la consulta:** se identifican las entidades de la pregunta, se recuperan sus vecinos a un salto y se añaden al contexto como "hechos" junto a los chunks.
3. Se documenta la comparación de una misma pregunta **con y sin grafo**.

---

## 1.8 Contrato F — Guardarraíles y multiagente (nivel Experto)

### Guardarraíles

Se aplican a todo contenido antes de devolverlo:

| Tipo | Comprobación |
|---|---|
| **Reglas (código)** | Longitud y número de hashtags según §1.4; idioma correcto |
| **LLM juez** | ¿Es ofensivo? ¿Da recomendaciones de inversión? En ciencia: ¿cada afirmación se apoya en las fuentes recuperadas? |

```json
"guardrails": {
  "passed": true,
  "checks": [
    { "name": "longitud", "passed": true },
    { "name": "ofensivo", "passed": true },
    { "name": "consejo_inversion", "passed": true }
  ]
}
```

Si una comprobación falla, se regenera **una vez**. Si sigue fallando, se devuelve con `passed: false` y el motivo, y la interfaz lo muestra.

### Multiagente (LangGraph)

```
petición libre → ROUTER → { social | finance | science } → GUARDARRAÍLES → ¿pasa?
                                                                ├─ sí → respuesta
                                                                └─ no → reintento (máx. 1)
```

- El **router** clasifica la petición (temperatura 0).
- Cada agente **reutiliza el servicio existente** de su área. No se duplica lógica.
- La respuesta indica qué agente la atendió.

---

## 1.9 Cobertura de la evaluación

| Criterio | Dónde se cumple |
|---|---|
| **Uso de modelos LLM** | Llama vía Ollama y Groq (T-1.1, T-1.3, T-2.1) |
| **Uso de frameworks para aplicaciones con LLMs** | LangChain (todo el backend), LangSmith (T-3.1), LangGraph (T-4.2) |
| **Prompt engineering** | Plantillas versionadas y medidas (T-1.4, T-1.8) |
| **Técnicas de PLN** | Generación de texto, extracción de palabras clave (T-2.3), generación multilingüe (T-3.3), resumen de datos (T-3.4), chunking, embeddings y búsqueda semántica (T-3.5, T-3.6), clasificación (T-4.1), extracción de entidades y relaciones (T-4.3) |

---

## 1.10 Fuera de alcance

- Usuarios, registro e inicio de sesión.
- Base de datos (salvo el índice del RAG).
- Publicación automática en las redes sociales.
- Entrenamiento o *fine-tuning* de modelos.
- Despliegue público de la aplicación.
- Después de la entrega: streaming, WebMCP, generación de imágenes con IA, lectura en voz alta e historial (ver extras en `3_tasks.md`).

---

## 1.11 Riesgos

| Riesgo | Mitigación |
|---|---|
| Ollama es lento sin GPU dedicada | Groq como proveedor por defecto; tiempo de respuesta visible en la interfaz |
| Groq alcanza su límite de peticiones | Error 429 claro; la ingesta del Graph RAG usa un subconjunto pequeño de chunks |
| Falla la wifi durante la exposición | Vídeo de la demo grabado; Ollama con el modelo ya cargado como alternativa |
| Documentación de Tailwind 3 mezclada con la 4 | Seguir solo documentación de Tailwind 4 |
| Retraso en el calendario | Plan de recorte en `3_tasks.md`; cada nivel termina con una versión completa y etiquetada |
