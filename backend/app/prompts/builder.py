"""Monta los mensajes del prompt a partir de las plantillas de templates/."""

import re
from pathlib import Path
from typing import Literal

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

TEMPLATES_DIR = Path(__file__).parent / "templates"
DEFAULT_LANGUAGE = "castellano (español de España)"

Platform = Literal["x", "instagram", "linkedin", "blog"]
Audience = Literal["general", "profesional", "juvenil", "infantil"]


VERSION_PATTERN = re.compile(r"<!--\s*version:\s*(\S+)\s*-->")


def load_template(name: str) -> tuple[str, str]:
    """Lee una plantilla y devuelve su versión y su texto, sin el comentario de versión."""
    raw = (TEMPLATES_DIR / name).read_text(encoding="utf-8")
    match = VERSION_PATTERN.search(raw)
    version = match.group(1) if match else "sin versión"
    text = VERSION_PATTERN.sub("", raw).strip()
    return version, text

def load_audiences() -> dict[str, str]:
    """Devuelve las reglas de cada audiencia, por ejemplo {"juvenil": "Público joven..."}."""
    _, text = load_template("audiences.md")
    audiences = {}
    for block in text.split("## ")[1:]:
        name, _, rules = block.partition("\n")
        audiences[name.strip()] = rules.strip()
    return audiences

def build_messages(
    topic: str,
    platform: Platform,
    audience: Audience,
    language: str = DEFAULT_LANGUAGE,
) -> list[BaseMessage]:
    """Monta el system prompt y el encargo para una plataforma y una audiencia."""
    _, system_text = load_template("system.md")
    _, platform_text = load_template(f"platforms/{platform}.md")
    audience_rules = load_audiences()[audience]

    return [
        SystemMessage(content=system_text.format(language=language)),
        HumanMessage(
            content=platform_text.format(topic=topic, audience_rules=audience_rules)
        ),
    ]


def get_prompt_versions(platform: Platform) -> dict[str, str]:
    """Versiones de las plantillas usadas para una plataforma, para registrarlas."""
    return {
        "system": load_template("system.md")[0],
        "platform": load_template(f"platforms/{platform}.md")[0],
        "audiences": load_template("audiences.md")[0],
    }