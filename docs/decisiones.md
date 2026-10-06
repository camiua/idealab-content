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