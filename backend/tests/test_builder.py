"""Tests del constructor de prompts: las 16 combinaciones generan un prompt completo."""

import re

import pytest
from langchain_core.messages import HumanMessage, SystemMessage

from app.prompts.builder import build_messages, get_prompt_versions

PLATFORMS = ["x", "instagram", "linkedin", "blog"]
AUDIENCES = ["general", "profesional", "juvenil", "infantil"]


@pytest.mark.parametrize("platform", PLATFORMS)
@pytest.mark.parametrize("audience", AUDIENCES)
def test_build_messages_for_every_combination(platform, audience):
    messages = build_messages("Café de especialidad", platform, audience)

    assert isinstance(messages[0], SystemMessage)
    assert isinstance(messages[-1], HumanMessage)
    full_prompt = "\n".join(message.content for message in messages)
    assert "Café de especialidad" in full_prompt
    assert "{" not in full_prompt, "Queda una variable de la plantilla sin rellenar"


def test_prompt_versions_are_registered():
    versions = get_prompt_versions("linkedin")

    assert set(versions) == {"system", "platform", "audiences"}
    for name, version in versions.items():
        assert re.fullmatch(r"v\d+", version), f"Versión mal escrita en {name}: {version}"