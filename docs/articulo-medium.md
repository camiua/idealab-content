# IdeaLab Content: cómo construí un generador de contenido con IA que comprueba lo que escribe

> Borrador del artículo para Medium. Se escribe por partes, una sección por nivel del proyecto.

## 1. El problema

Digital Content es una agencia que publica a diario en blogs, Instagram, LinkedIn y X. Cada red tiene sus propias reglas: X corta a los 280 caracteres (y cuenta cada emoji como dos), Instagram esconde el texto tras unos 125 caracteres, LinkedIn solo enseña unos 200 antes del «… ver más», y un blog necesita estructura, un título de menos de 60 caracteres y una meta descripción para posicionarse. Escribir bien para cada red, y para públicos distintos, lleva tiempo.

La pregunta de partida era sencilla: **¿puede un modelo de lenguaje escribir posts listos para publicar, que cumplan las reglas de cada red con la mínima revisión manual?** Con una condición: usar solo modelos locales o APIs gratuitas.

Pronto descubrí que pedírselo al modelo no basta. Los LLM procesan el texto en *tokens*, fragmentos de palabras, y no letra a letra, así que les cuesta contar caracteres con precisión. Además, inventan: datos, cifras y hasta experiencias personales que nunca ocurrieron. Por eso el proyecto no consiste solo en generar texto, sino en **comprobar lo que genera y medir si mejora**.

El proyecto se construye por niveles, de Esencial a Experto. Este artículo sigue el mismo camino: cada sección cuenta un nivel.

## 2. La arquitectura

![Arquitectura de IdeaLab Content](arquitectura.png)

El sistema tiene dos partes que se comunican por una API:

- **Frontend (React, Vite y Tailwind CSS).** Un formulario donde se elige el tema, la plataforma, la audiencia y el modelo. Muestra el post con sus métricas: el modelo usado, el tiempo de respuesta y, en X, el recuento de caracteres con la regla de la propia red (los emojis cuentan dos).
- **Backend (Python, FastAPI y LangChain)**, organizado en capas que no se mezclan:
  - **Rutas:** validan la petición y devuelven errores claros si un modelo no responde.
  - **Servicio de generación:** construye el prompt, llama al modelo, **comprueba las reglas con código** (longitud, hashtags, palabras y meta descripción) y, si alguna falla, lo regenera una vez indicándole el error concreto.
  - **Plantillas de prompt:** fuera del código, en archivos Markdown con versión: un prompt común, uno por plataforma y uno por audiencia.
  - **Proveedores:** un único punto de acceso al modelo, con dos opciones intercambiables.

**¿Por qué dos modelos?** En la primera prueba, el mismo post tardó **unos 30 segundos** con Llama 3.2 (3B) en local, con Ollama en un portátil sin GPU (35,7 s la primera vez, porque incluía cargar el modelo), y **2 segundos** con gpt-oss-120b en Groq. Groq es la opción por defecto; Ollama demuestra que la aplicación puede funcionar sin internet ni claves.

Todo el diseño se escribió antes de programar, con **desarrollo guiado por especificaciones**: un documento de qué se construye, otro de cómo se organiza y una lista de tareas con su criterio de "hecho". Cada tarea tuvo su issue, su rama y su pull request.

*Próxima sección: cómo medí la calidad de los prompts con un banco de pruebas, y por qué un 100 % de cumplimiento escondía un problema.*