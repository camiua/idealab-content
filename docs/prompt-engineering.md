# Prompt engineering: evolución de las plantillas

Este documento registra cómo han cambiado los prompts y **qué efecto ha tenido cada cambio, medido con el banco de pruebas**. Cada versión se justifica con datos, no con intuiciones.

## Cómo se mide

Script: `backend/scripts/eval_prompts.py`. Desde `backend/`:

```bash
uv run python -m scripts.eval_prompts --label v2-run1            # genera y evalúa
uv run python -m scripts.eval_prompts --label v2-run1 --rescore  # solo reevalúa un CSV
```

- **Condiciones fijas:** 5 temas × 4 plataformas = 20 posts por ejecución, audiencia general, Groq `openai/gpt-oss-120b`, temperatura 0,7.
- **Se mide el primer intento**, sin el reintento de la app, para evaluar el prompt y no el sistema de reintentos.
- **Dos ejecuciones por versión (40 posts).** Con temperatura 0,7 cada ejecución da resultados distintos; una sola no permite sacar conclusiones.
- **Reglas de formato:** las mismas que usa la app (`check_rules`): longitud, hashtags, palabras del blog y meta descripción.
- **Métricas de calidad** (detectores con patrones): experiencia inventada en primera persona, anglicismos, vocabulario latinoamericano y cifras.
- Resultados completos (los 20 posts de cada ejecución) en `docs/eval/*.csv`; resúmenes en `docs/eval/*.md`.

## v1: reglas de formato por plataforma

Plantillas iniciales (T-1.4): un `system.md` común, una plantilla por plataforma y una por audiencia.

**Resultado:** las reglas de formato se cumplen casi siempre (39 de 40). Pero al leer los posts uno a uno aparecen fallos que esas reglas no miden:

- **Experiencias personales inventadas en LinkedIn:** *"Personalmente, la primera vez que probé un café de Etiopía…"*, *"En mi experiencia como formador…"*, *"En mi último mes de pruebas, separé…"*. Digital Content publica en nombre de marcas: son vivencias que no existen.
- **Vocabulario latinoamericano** pese a pedir "español de España": *empaques*, *brinda*, *corporativos*, *sustentable*.
- **Anglicismos**, también en hashtags: `#EcoTips`, *laptop*, *pour-over*.
- **Cifras sin fuente:** *"reduce hasta un 30 % tus residuos"*, *"cada kilo de papel reciclado ahorra más de 10 m³ de agua"*.

Por eso se añadieron al banco de pruebas las cuatro métricas de calidad.

## v2: voz de marca y vocabulario de España

Cambios en `system.md` (aplican a todas las plataformas):

- Escribir en nombre de una marca: sin experiencias ni anécdotas en primera persona del singular. Alternativa: hablar en plural o dirigirse al lector.
- Sin cifras, porcentajes ni estudios concretos que no estén en el tema.
- Vocabulario de España, con ejemplos (*envases* y no *empaques*, *ofrecer* y no *brindar*…).
- Sin anglicismos si existe palabra en español, también en los hashtags.

Refuerzo en `platforms/linkedin.md`, donde se concentraba el fallo: hablar como la marca y, si hay un ejemplo, que sea claramente hipotético.

Cada regla nace de un fallo medido y da una alternativa, no solo una prohibición.

## Resultados: v1 frente a v2

| Métrica (40 posts por versión) | v1 | v2 |
|---|---|---|
| Cumplen las reglas de formato | 39 / 40 | 39 / 40 |
| **Experiencia inventada** | **7** (7 de 10 en LinkedIn) | **0** |
| Anglicismos | 4 | 2 |
| Vocabulario latinoamericano | 3 | 1 |
| Cifras | 3 | 1 |

Detalle por ejecución: `docs/eval/v1-run1.md`, `v1-run2.md`, `v2-run1.md` y `v2-run2.md`.

## Conclusiones

- **La experiencia inventada desaparece (7 → 0).** Es el cambio más claro: el fallo era estable en la v1 (3–4 de 5 posts de LinkedIn en cada ejecución) y no aparece en ninguna de la v2.
- **Anglicismos, vocabulario y cifras bajan**, pero con tan pocos casos (de 1 a 4) es una tendencia, no una conclusión firme.
- **Las reglas de formato no empeoran.** Los fallos son puntuales y distintos en cada ejecución: un blog vacío en la v1 y un blog de 831 palabras en la v2.

## Límites y aprendizajes

- **Una métrica también hay que evaluarla.** La primera versión del detector de experiencia inventada no detectaba *"Yo empecé…"* ni *"separé…"*. Se comprobó leyendo los posts y se corrigió; con `--rescore` se reevaluaron las ejecuciones anteriores sin volver a llamar al modelo.
- **Los detectores buscan palabras concretas.** El modelo podría inventar experiencias con otras palabras (*"nuestro equipo probó…"*). Por eso los resultados se revisan también leyendo los posts: si una métrica se convierte en el objetivo, deja de medir bien (ley de Goodhart).
- **Solo se mide la audiencia general.** Las cifras inventadas más llamativas (informes y salarios inventados) aparecieron en pruebas con audiencia profesional, que el banco no cubre.
- **Hay fallos que no se pueden medir con patrones:** errores sobre España (el vidrio va al contenedor verde, no al amarillo) o consejos desfasados (cambiar la contraseña cada tres meses). Necesitan conocimiento real: son el motivo de los guardarraíles del nivel experto.
- **Respuesta vacía:** en una ejecución, el blog llegó vacío. `gpt-oss-120b` es un modelo de razonamiento y a veces gasta su presupuesto de tokens pensando. En la app lo cubre el reintento; en el banco se mide sin él.