"""Genera un post: monta el prompt, llama al modelo y comprueba las reglas de la plataforma."""

import re
from dataclasses import dataclass

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage

from app.prompts.builder import (
    Audience,
    Platform,
    build_messages,
    get_prompt_versions,
    load_template,
)

# Reglas de la spec §1.4 que se pueden comprobar con código
MAX_CHARS = {"x": 280, "instagram": 2200, "linkedin": 3000}
HASHTAGS = {"x": (1, 2), "instagram": (3, 5), "linkedin": (3, 5), "blog": (0, 0)}
BLOG_WORDS = (500, 800)
META_PREFIX = "Meta descripción:"
META_MAX = 160

HASHTAG_PATTERN = re.compile(r"#\w+")


@dataclass
class GenerationResult:
    content: str
    warnings: list[str]
    prompt_versions: dict[str, str]


def x_length(text: str) -> int:
    """Longitud aproximada según X: letras y signos valen 1; emojis y otros símbolos, 2."""
    length = 0
    for char in text:
        code = ord(char)
        if code in (0x200D, 0xFE0F): # piezas invisibles que forman los emojis
           continue
        length += 1 if code <= 0x10FF else 2 
    return length

def check_rules(text: str, platform: Platform) -> list[str]:
    """Devuelve la lista de reglas que el texto incumple. Vacía si cumple todas."""
    problems = []
    
    if platform == "x" and x_length(text) > MAX_CHARS["x"]:
        problems.append(f"Tiene {x_length(text)} caracteres según el recuento de X; el máximo es 280.")
    elif platform in ("instagram", "linkedin") and len(text) > MAX_CHARS[platform]:
        problems.append(f"Tiene {len(text)} caracteres; el máximo es {MAX_CHARS[platform]}.")
        
    hashtags = len(HASHTAG_PATTERN.findall(text))
    low, high = HASHTAGS[platform]
    if not low <= hashtags <= high:
        expected = "ninguno" if high == 0 else f"entre {low} y {high}"
        problems.append(f"Tiene {hashtags} hashtags; deben ser {expected}.")
    
    if platform == "blog":
        words = len(text.split())
        if not BLOG_WORDS[0] <= words <= BLOG_WORDS[1]:
            problems.append(f"Tiene {words} palabras; deben ser entre 500 y 800.")
        first_line = text.splitlines()[0] if text else ""
        if not first_line.startswith(META_PREFIX):
            problems.append(f'La primera línea debe empezar por "{META_PREFIX}".')
        elif len(first_line.removeprefix(META_PREFIX).strip()) > META_MAX:
            problems.append(f"La meta descripción supera los {META_MAX} caracteres.")
            
    return problems


def generate_post(
    topic: str,
    platform: Platform,
    audience: Audience,
    model: BaseChatModel,
) -> GenerationResult:
    """Genera el post y, si incumple alguna regla, lo regenera una vez indicando el error."""
    messages = build_messages(topic, platform, audience)
    content = model.invoke(messages).content.strip()
    problems = check_rules(content, platform)
    
    if problems:
        _, retry_text = load_template("retry.md")
        retry = retry_text.format(problems="\n".join(f"- {p}" for p in problems))
        messages += [AIMessage(content=content), HumanMessage(content=retry)]
        content = model.invoke(messages).content.strip()
        problems = check_rules(content, platform)
        
    return GenerationResult(
        content=content,
        warnings=problems,
        prompt_versions=get_prompt_versions(platform),
    )