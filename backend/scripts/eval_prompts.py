"""Banco de pruebas de prompts (T-1.8).

Genera un post por cada combinación de tema y plataforma, siempre en las mismas
condiciones (mismo modelo, temperatura y audiencia), y comprueba cada uno con las
mismas reglas que usa la app (check_rules). Mide el PRIMER intento, sin reintento:
así se evalúa la calidad del prompt y no la del sistema de reintentos.

Uso, desde backend/:
    uv run python -m scripts.eval_prompts --label v1-run1            # genera y evalúa
    uv run python -m scripts.eval_prompts --label v1-run1 --rescore  # solo reevalúa el CSV
"""

import argparse
import csv
import re
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

from app.llm.providers import get_chat_model, get_model_name, is_rate_limit_error
from app.prompts.builder import build_messages, get_prompt_versions
from app.services.generation import check_rules

# Condiciones fijas: si cambian, las versiones dejan de ser comparables
TOPICS = [
    "Café de especialidad",
    "Teletrabajo y salud",
    "Ciberseguridad para pequeñas empresas",
    "Reciclaje en casa",
    "Inteligencia artificial en la educación",
]
PLATFORMS = ["x", "instagram", "linkedin", "blog"]
AUDIENCE = "general"
PROVIDER = "groq"
TEMPERATURE = 0.7

PAUSE_SECONDS = 2  # pausa entre llamadas para no chocar con el límite gratuito de Groq
RATE_LIMIT_WAIT = 30  # espera si Groq devuelve 429
RESULTS_DIR = Path(__file__).resolve().parents[2] / "docs" / "eval"

# Métricas de calidad que las reglas de formato no miden.
# Son aproximaciones con patrones: no detectan todos los casos, pero sí miden
# lo mismo en todas las versiones, que es lo que hace falta para comparar.
ENGLISH_WORDS = {
    "coffee", "lovers", "lover", "shop", "the", "and", "your", "you", "with",
    "life", "style", "lifestyle", "mindset", "tips", "vibes", "goals", "love",
    "laptop", "grinder", "pour", "over",
}
LATAM_WORDS = {
    "empaque", "empaques", "brinda", "brindan", "brindar", "corporativos",
    "computadora", "computadoras", "celular", "celulares", "platicar", "jugo", "jugos",
    "sustentable", "sustentables",
}
# Primera persona del singular: la marca no tiene vivencias propias
FIRST_PERSON = re.compile(
    r"\b(yo|personalmente|en mi experiencia|me ha funcionado|mi (?:experiencia|último|primera|momento)"
    r"|empecé|probé|descubrí|aprendí|comprendí|separé|decidí|noté|recuerdo cuando)\b",
    re.IGNORECASE,
)
FIGURES = re.compile(
    r"\d+(?:[.,]\d+)*\s?(?:%|€|euros|millones|m³)|según (?:el|la|un|una) (?:informe|estudio|encuesta)",
    re.IGNORECASE,
)
WORD_PATTERN = re.compile(r"[a-záéíóúüñ]+", re.IGNORECASE)


def find_words(text: str, vocabulary: set[str]) -> list[str]:
    """Palabras de la lista que aparecen en el texto, también dentro de hashtags."""
    # Separa los hashtags en palabras: #CoffeeLovers -> Coffee Lovers
    spaced = re.sub(r"(?<=[a-záéíóúñ])(?=[A-ZÁÉÍÓÚÑ])", " ", text)
    words = {word.lower() for word in WORD_PATTERN.findall(spaced)}
    return sorted(words & vocabulary)


def find_matches(text: str, pattern: re.Pattern) -> list[str]:
    """Fragmentos del texto que encajan con el patrón (sin repetir)."""
    return sorted({match.group(0).lower() for match in pattern.finditer(text)})


QUALITY_CHECKS = {
    "english_words": ("Anglicismos", lambda text: find_words(text, ENGLISH_WORDS)),
    "latam_words": ("Vocabulario latinoamericano", lambda text: find_words(text, LATAM_WORDS)),
    "first_person": ("Experiencia inventada", lambda text: find_matches(text, FIRST_PERSON)),
    "figures": ("Cifras", lambda text: find_matches(text, FIGURES)),
}


def invoke_once(model, messages) -> str:
    """Una sola generación. Si Groq pide esperar (429), espera y lo vuelve a intentar."""
    for attempt in range(3):
        try:
            return model.invoke(messages).content
        except Exception as exc:
            if is_rate_limit_error(exc) and attempt < 2:
                print(f"   Límite de Groq: espero {RATE_LIMIT_WAIT} s…")
                time.sleep(RATE_LIMIT_WAIT)
                continue
            raise


def run(label: str) -> list[dict]:
    model = get_chat_model(PROVIDER, temperature=TEMPERATURE)
    rows = []
    total = len(TOPICS) * len(PLATFORMS)

    for topic in TOPICS:
        for platform in PLATFORMS:
            messages = build_messages(topic, platform, AUDIENCE)
            start = time.perf_counter()
            text = invoke_once(model, messages)
            elapsed_ms = int((time.perf_counter() - start) * 1000)

            problems = check_rules(text, platform)
            quality = {key: check(text) for key, (_, check) in QUALITY_CHECKS.items()}
            rows.append(
                {
                    "label": label,
                    "topic": topic,
                    "platform": platform,
                    "passed": not problems,
                    "problems": " | ".join(problems),
                    **{key: " | ".join(found) for key, found in quality.items()},
                    "elapsed_ms": elapsed_ms,
                    "prompt_versions": " ".join(f"{k}={v}" for k, v in get_prompt_versions(platform).items()),
                    "content": text,
                }
            )
            mark = "OK   " if not problems else "FALLA"
            print(f"[{len(rows):>2}/{total}] {mark} {platform:<9} {topic}" + (f" → {problems}" if problems else ""))
            time.sleep(PAUSE_SECONDS)

    return rows


def summary_markdown(label: str, rows: list[dict]) -> str:
    lines = [
        f"# Banco de pruebas · {label}",
        "",
        f"- Fecha: {datetime.now():%Y-%m-%d %H:%M}",
        f"- Modelo: {PROVIDER} · {get_model_name(PROVIDER)} · temperatura {TEMPERATURE}",
        f"- Audiencia: {AUDIENCE} · {len(TOPICS)} temas × {len(PLATFORMS)} plataformas = {len(rows)} posts",
        "- Se mide el primer intento, sin reintento.",
        "",
        "| Plataforma | Cumplen las reglas | % | "
        + " | ".join(name for name, _ in QUALITY_CHECKS.values())
        + " |",
        "|---|---|---|" + "---|" * len(QUALITY_CHECKS),
    ]
    for platform in PLATFORMS + ["total"]:
        group = rows if platform == "total" else [r for r in rows if r["platform"] == platform]
        passed = sum(r["passed"] for r in group)
        quality = " | ".join(str(sum(bool(r[key]) for r in group)) for key in QUALITY_CHECKS)
        name = "**Total**" if platform == "total" else platform
        lines.append(f"| {name} | {passed} / {len(group)} | {100 * passed / len(group):.0f} % | {quality} |")

    lines += ["", "Las columnas de calidad cuentan los posts en los que aparece al menos un caso."]

    problems = Counter(p for r in rows for p in r["problems"].split(" | ") if p)
    if problems:
        lines += ["", "## Fallos más frecuentes", ""]
        lines += [f"- {count} × {problem}" for problem, count in problems.most_common(10)]

    return "\n".join(lines) + "\n"


def save(label: str, rows: list[dict]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = RESULTS_DIR / f"{label}.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    md_path = RESULTS_DIR / f"{label}.md"
    md_path.write_text(summary_markdown(label, rows), encoding="utf-8")
    print(f"\nResultados guardados en {csv_path} y {md_path}")


def rescore(label: str) -> list[dict]:
    """Vuelve a evaluar un CSV ya generado, sin llamar al modelo.

    Sirve para mejorar las métricas y aplicarlas a ejecuciones anteriores gratis:
    generar y evaluar son dos pasos separados.
    """
    with (RESULTS_DIR / f"{label}.csv").open(encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    for row in rows:
        row["passed"] = not check_rules(row["content"], row["platform"])
        row["problems"] = " | ".join(check_rules(row["content"], row["platform"]))
        for key, (_, check) in QUALITY_CHECKS.items():
            row[key] = " | ".join(check(row["content"]))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Banco de pruebas de prompts")
    parser.add_argument("--label", required=True, help="Nombre de la ejecución, p. ej. v1-run1")
    parser.add_argument("--rescore", action="store_true", help="Reevalúa el CSV existente sin llamar al modelo")
    args = parser.parse_args()

    rows = rescore(args.label) if args.rescore else run(args.label)
    save(args.label, rows)
    print()
    print(summary_markdown(args.label, rows))


if __name__ == "__main__":
    main()