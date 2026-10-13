# Decisiones y aprendizajes

Complementa las decisiones de arquitectura de [`.specify/1_spec.md`](../.specify/1_spec.md) §1.2
con lo aprendido durante el desarrollo. Cada aprendizaje indica la tarea en la que surgió.

## Aprendizajes

### Spike de generación con Ollama y Groq (T-1.1)

Mismo prompt (post de Instagram para una cafetería de Madrid), temperatura 0,7.

| Proveedor | Modelo | Tiempo | Tokens entrada / salida |
|---|---|---|---|
| Ollama (local, CPU sin GPU dedicada) | `llama3.2` (3B) | 35,7 s (1.ª ejecución) · 30,0 s (2.ª) | 87 / ~110 |
| Groq (nube) | `openai/gpt-oss-120b` | 2,0 s | 131 / 602 |

- **Groq es ~15 veces más rápido** en el equipo de desarrollo. Confirma la decisión D-3: Groq como proveedor por defecto en la demo.
- **gpt-oss es un modelo de razonamiento:** antes de responder genera un razonamiento interno que también cuenta como tokens de salida (602 tokens para un post de unas 80 palabras).
- **El modelo pequeño alucina y comete errores de lenguaje:**
  - Alucinación: *"granos de las mejores granjas de España"* (en España no se cultiva café a escala comercial).
  - Errores: *"desperta"*, *"#VivaLaCafé"*.
  - El modelo grande también falla a veces (*"buencafé"*). Ambos casos justifican los guardarraíles del nivel Experto.
- **Variedad del español:** sin indicarlo, el modelo mezcla variedades (en una prueba sonaba argentino). Con *"castellano (español de España)"* en el system prompt, los posts suenan a España.

### Cambio de modelo en Groq (T-1.1)

- El plan gratuito de Groq **ya no incluye modelos Llama de chat**: `llama-3.1-8b-instant` devolvía `404 model_not_found`.
- Se consultaron los modelos disponibles con la API (`/openai/v1/models`) y se eligió **`openai/gpt-oss-120b`**, también de pesos abiertos.
- Haber dejado el modelo configurable en el `.env` permitió cambiarlo sin tocar el código.

### Entorno de desarrollo (T-1.1)

- `load_dotenv()` **no sobrescribe** variables que ya existen en el entorno: si se cargan con `source .env` en una terminal, los cambios posteriores del `.env` no se aplican hasta abrir otra terminal.
- Las dependencias del spike se declaran en el propio script (cabecera `# /// script`) y `uv run` crea un entorno temporal, sin instalar nada en el proyecto.

### Proyecto backend (T-1.2)

- **Entorno virtual fuera de OneDrive:** el repositorio está en una carpeta sincronizada y un `.venv` con
  miles de archivos la ralentiza. Con `UV_PROJECT_ENVIRONMENT` (en `.vscode/settings.json`, que no se sube)
  uv crea el entorno en `C:\Users\<usuario>\.venvs\idealab-backend`.
- **`pyproject.toml` + `uv.lock`:** el primero declara qué librerías usa el proyecto; el segundo fija las
  versiones exactas de todas, incluidas las indirectas. Con `uv sync` cualquiera recrea el mismo entorno.
- **`SecretStr` para las claves:** si se imprime la configuración, la clave de Groq aparece como `**********`.
- **`develop` como rama por defecto:** `Closes #N` en un PR hacia `develop` cierra la issue y el tablero la
  mueve a *Done* automáticamente.

### Punto único de acceso al LLM (T-1.3)

- **Patrón Factory:** `get_chat_model(provider)` es la única función que crea modelos. El resto del código
  usa la interfaz común de LangChain (`BaseChatModel` y `.invoke`) sin saber qué proveedor hay detrás.
  Cambiar de modelo o añadir un proveedor solo afecta a `llm/providers.py`.
- **Misma petición, distinta calidad** ("Saluda en 5 palabras"):

  | Proveedor | Respuesta | Observación |
  |---|---|---|
  | Groq · gpt-oss-120b | "¡Hola! ¿Cómo te encuentras hoy?" | 5 palabras, correcto |
  | Ollama · Llama 3.2 (3B) | "¡Hola, soy aquí para ayudarte!" | 6 palabras y error gramatical ("soy aquí") |

  Confirma lo visto en T-1.1: el modelo pequeño comete más errores de idioma y sigue peor las
  restricciones. Refuerza la decisión de usar Groq como proveedor por defecto.
- **Fallar pronto:** `DEFAULT_PROVIDER` se tipa con `Literal["ollama", "groq"]`. Un valor mal escrito en el
  `.env` impide arrancar la app con un mensaje claro, en lugar de fallar más tarde en mitad de una petición.

### Plantillas de prompt v1 (T-1.4)

- **Prompts fuera del código:** cada plantilla es un archivo Markdown en `prompts/templates/` con su versión
  en un comentario (`<!-- version: v1 -->`). Se pueden leer y mejorar sin tocar Python, y Git muestra
  exactamente qué cambió entre versiones.
- **Prompt común + prompt por plataforma:** las reglas generales (rol, idioma, no inventar datos) están en
  `system.md` y se aplican a todas las peticiones; cada plataforma añade sus propias reglas. Así no se
  repiten reglas y cada pieza se mejora por separado.
- **Restricciones concretas:** "máximo 280 caracteres, contando espacios y hashtags" en lugar de
"un post corto". Aun así, el modelo puede no cumplirlas, por lo que las reglas también se comprueban con
  código después de generar (T-1.5).
- **v1 *zero-shot* a propósito:**
  - *Zero-shot*: solo instrucciones, sin ejemplos.
  - *Few-shot*: instrucciones y uno o varios ejemplos de buen resultado. Suele mejorar el formato y el tono.

  La v1 se escribe sin ejemplos para tener una **línea base medible**. El banco de pruebas (T-1.8) indicará
  qué reglas se incumplen y, si hace falta, la v2 añadirá ejemplos (*few-shot*). La comparación entre
  versiones se registra en `docs/prompt-engineering.md`.

### Errores anticipados por plataforma (T-1.4)

Las plantillas incluyen reglas para evitar errores que obligarían a corregir el texto a mano antes de publicarlo:

| Plataforma | Error típico | Regla en el prompt |
|---|---|---|
| X | Contar los emojis como 1 carácter: X los cuenta como 2 y rechaza el post | "Cada emoji cuenta como 2 caracteres". El servicio (T-1.5) lo comprueba igual |
| Instagram | Gancho cortado: Instagram oculta el texto tras unos 125 caracteres | Primera frase de menos de 125 caracteres |
| LinkedIn | Gancho cortado: LinkedIn oculta el texto tras unos 200 caracteres | Las dos primeras líneas enganchan por sí solas |
| Blog | Título cortado en Google hacia los 60 caracteres | Título de 60 caracteres como máximo |
| Todas | Hashtags rotos por espacios o guiones (`#café-de-barrio`) | Hashtags de una sola palabra |
| Todas | Huecos sin rellenar ("[nombre de la empresa]") o enlaces inventados | Sin huecos ni URLs (`system.md`) |

### Buenas prácticas en aplicaciones con LLMs

Prácticas habituales en el desarrollo con LLMs y dónde se aplican en el proyecto:

| Práctica | Por qué | Dónde |
|---|---|---|
| **Prompt común + prompt específico por plataforma** | Las reglas generales se escriben una sola vez y cada plataforma añade las suyas. Cada pieza se mejora por separado. | T-1.4: `system.md` + `platforms/*.md` |
| **Medir en lugar de opinar** | Una mejora en un prompt solo es real si se puede medir. Las versiones se comparan con evaluaciones automatizadas, en las mismas condiciones: mismos temas, modelo y temperatura. | T-1.8: banco de pruebas, v1 frente a v2 |
| **Observabilidad** | Con LangSmith, cada llamada al modelo queda registrada (prompt, respuesta, tiempo y tokens) sin cambiar el código. Permite revisar por qué un resultado salió mal. | T-3.1 |
| **Agentes especializados por tipo de trabajo** | Un agente tiene sentido cuando cambia la tarea (consultar datos de bolsa, buscar en papers), no cuando solo cambian las reglas del texto, que ya resuelven las plantillas. | T-4.2: agentes de redes sociales, finanzas y ciencia |
| **No depender de un único servicio** | Los planes gratuitos cambian a menudo (Groq retiró Llama). El modelo es configurable en el `.env`, el patrón Factory aísla a cada proveedor y Ollama funciona en local como alternativa. | T-1.3: `llm/providers.py` |