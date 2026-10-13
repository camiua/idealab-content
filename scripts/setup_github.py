"""Crea en GitHub los labels, milestones e issues del proyecto a partir de .specify/3_tasks.md.

Así las issues no pueden desincronizarse de las tareas: salen del mismo archivo.
Se puede ejecutar varias veces sin duplicar nada (es idempotente).

Requisitos: GitHub CLI instalado y con sesión iniciada (`gh auth login`).

Uso, desde la raíz del repositorio:
    python scripts/setup_github.py --dry-run   # solo muestra lo que haría
    python scripts/setup_github.py             # lo crea de verdad
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

TASKS_FILE = Path(".specify/3_tasks.md")

# Nombre, color (hex sin #) y descripción de cada label.
LABELS = [
    ("fase:0-arranque", "D3D1C7", "Fase 0: arranque"),
    ("fase:1-esencial", "97C459", "Fase 1: nivel esencial"),
    ("fase:2-medio", "EF9F27", "Fase 2: nivel medio"),
    ("fase:3-avanzado", "D85A30", "Fase 3: nivel avanzado"),
    ("fase:4-experto", "E24B4A", "Fase 4: nivel experto"),
    ("fase:5-entrega", "B4B2A9", "Fase 5: entrega y exposición"),
    ("extras", "AFA9EC", "Mejoras para después de la entrega"),
    ("nivel:esencial", "97C459", "Requisito del nivel esencial"),
    ("nivel:medio", "EF9F27", "Requisito del nivel medio"),
    ("nivel:avanzado", "D85A30", "Requisito del nivel avanzado"),
    ("nivel:experto", "E24B4A", "Requisito del nivel experto"),
    ("nivel:mejora", "7F77DD", "Mejora de producto fuera del briefing"),
    ("nivel:seguridad", "A32D2D", "Seguridad"),
    ("nivel:soporte", "888780", "Organización, entorno y documentación"),
    ("gate", "501313", "Hito bloqueante: no se avanza sin cumplirlo"),
]

# Milestone por fase: título, descripción y fecha límite (fin del día en Madrid, en UTC).
MILESTONES = {
    "0": ("Arranque", "Repositorio, specs, issues y entorno", "2026-10-03T21:59:59Z"),
    "1": ("Nivel Esencial", "Posts por plataforma y audiencia con interfaz web", "2026-10-05T21:59:59Z"),
    "2": ("Nivel Medio", "Selector de modelo, perfil de empresa, imágenes y Docker", "2026-10-06T21:59:59Z"),
    "3": ("Nivel Avanzado", "LangSmith, idiomas, finanzas y RAG científico", "2026-10-08T21:59:59Z"),
    "4": ("Nivel Experto", "Guardarraíles, multiagente y Graph RAG", "2026-10-10T21:59:59Z"),
    "5": ("Entrega", "Documentación, entrega y exposición", "2026-10-14T21:59:59Z"),
    "E": ("Extras", "Mejoras para después de la entrega", None),
}

PHASE_LABEL = {
    "0": "fase:0-arranque",
    "1": "fase:1-esencial",
    "2": "fase:2-medio",
    "3": "fase:3-avanzado",
    "4": "fase:4-experto",
    "5": "fase:5-entrega",
    "E": "extras",
}

# Emoji de la leyenda → (label, texto para la issue).
LEVELS = {
    "🟢": ("nivel:esencial", "🟢 Esencial"),
    "🟡": ("nivel:medio", "🟡 Medio"),
    "🟠": ("nivel:avanzado", "🟠 Avanzado"),
    "🔴": ("nivel:experto", "🔴 Experto"),
    "⭐": ("nivel:mejora", "⭐ Mejora de producto"),
    "🔐": ("nivel:seguridad", "🔐 Seguridad"),
    "⚪": ("nivel:soporte", "⚪ Soporte"),
}
DEFAULT_LEVEL = ("nivel:soporte", "⚪ Soporte")

HEADER = re.compile(r"^\*\*((?:T|E)-[\w.]+) · (.+?)\*\*(.*)$")


def gh(*args: str, check: bool = True) -> str:
    """Ejecuta un comando de GitHub CLI y devuelve su salida."""
    result = subprocess.run(
        ["gh", *args], capture_output=True, text=True, encoding="utf-8", check=False
    )
    if check and result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return result.stdout


def parse_tasks(text: str) -> list[dict]:
    """Convierte 3_tasks.md en una lista de tareas."""
    tasks = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        match = HEADER.match(lines[i])
        if not match:
            i += 1
            continue
        task_id, title, meta = match.groups()
        block = []
        i += 1
        while i < len(lines) and lines[i].strip() and not HEADER.match(lines[i]):
            block.append(lines[i])
            i += 1

        phase = "E" if task_id.startswith("E-") else task_id.split("-")[1].split(".")[0]
        label, level_text = next(
            (value for emoji, value in LEVELS.items() if emoji in meta), DEFAULT_LEVEL
        )
        dep = re.search(r"dep: ([^·—]+)", meta)
        day = re.search(r"· ((?:lun|mar|mié|jue|vie|sáb|dom) \d+[^·]*)", meta)
        inline_desc = meta.split("—", 1)[1].strip() if "—" in meta else ""

        concepts, done, description = "", "", []
        for line in block:
            if line.startswith("*Conceptos:*"):
                concepts = line.removeprefix("*Conceptos:*").strip()
            elif line.startswith("*Hecho:*"):
                done = line.removeprefix("*Hecho:*").strip()
            else:
                description.append(line)
        if inline_desc:
            description.insert(0, inline_desc)

        tasks.append(
            {
                "id": task_id,
                "title": f"{task_id} · {title.strip()}",
                "phase": phase,
                "labels": [PHASE_LABEL[phase], label] + (["gate"] if "GATE" in task_id else []),
                "level": level_text,
                "description": " ".join(description).strip(),
                "concepts": concepts,
                "done": done,
                "dep": dep.group(1).strip() if dep else "",
                "day": day.group(1).strip() if day else "",
            }
        )
    return tasks


def capitalize(text: str) -> str:
    """Pone en mayúscula la primera letra sin tocar el resto."""
    return text[:1].upper() + text[1:]


def issue_body(task: dict) -> str:
    """Construye el cuerpo de la issue con la misma estructura que la plantilla."""
    parts = [f"## Tarea\n{task['title']}", f"## Nivel\n{task['level']}"]
    if task["day"]:
        parts.append(f"## Día previsto\n{task['day']}")
    if task["description"]:
        parts.append(f"## Descripción\n{capitalize(task['description'])}")
    if task["concepts"]:
        parts.append(f"## Conceptos\n{capitalize(task['concepts'])}")
    if task["done"]:
        parts.append(f"## Hecho cuando\n- [ ] {capitalize(task['done'])}")
    if task["dep"]:
        parts.append(f"## Dependencias\n{task['dep']}")
    parts.append("---\nDiseño: `.specify/1_spec.md` · Desglose: `.specify/3_tasks.md`")
    return "\n\n".join(parts)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="muestra lo que haría sin crear nada")
    args = parser.parse_args()

    if not TASKS_FILE.exists():
        sys.exit(f"No encuentro {TASKS_FILE}. Ejecuta el script desde la raíz del repositorio.")

    tasks = parse_tasks(TASKS_FILE.read_text(encoding="utf-8"))
    print(f"==> {len(tasks)} tareas encontradas en {TASKS_FILE}")

    if args.dry_run:
        for task in tasks:
            milestone = MILESTONES[task["phase"]][0]
            print(f"  {task['title']}\n      labels: {', '.join(task['labels'])} · milestone: {milestone}")
        print("\nModo prueba: no se ha creado nada.")
        return

    print("==> Labels")
    for name, color, description in LABELS:
        gh("label", "create", name, "--color", color, "--description", description, "--force")
        print(f"  ok  {name}")

    print("==> Milestones")
    existing = {m["title"] for m in json.loads(gh("api", "repos/{owner}/{repo}/milestones?state=all"))}
    for title, description, due_on in MILESTONES.values():
        if title in existing:
            print(f"  --  {title} (ya existe)")
            continue
        fields = ["-f", f"title={title}", "-f", f"description={description}"]
        if due_on:
            fields += ["-f", f"due_on={due_on}"]
        gh("api", "repos/{owner}/{repo}/milestones", *fields)
        print(f"  ok  {title}")

    print("==> Issues")
    existing = {
        issue["title"]
        for issue in json.loads(gh("issue", "list", "--state", "all", "--limit", "500", "--json", "title"))
    }
    created = 0
    for task in tasks:
        if task["title"] in existing:
            print(f"  --  {task['id']} (ya existe)")
            continue
        try:
            gh(
                "issue", "create",
                "--title", task["title"],
                "--body", issue_body(task),
                "--label", ",".join(task["labels"]),
                "--milestone", MILESTONES[task["phase"]][0],
            )
            print(f"  ok  {task['id']}")
            created += 1
        except RuntimeError as error:
            print(f"  ERR {task['id']}: {str(error)[:100]}")

    print(f"\n==> {created} issues creadas.")


if __name__ == "__main__":
    main()
