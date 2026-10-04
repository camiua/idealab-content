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