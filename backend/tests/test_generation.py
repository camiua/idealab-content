"""Tests del servicio de generación con un modelo falso: sin red, sin coste y siempre igual."""

from langchain_core.language_models import FakeListChatModel

from app.services.generation import check_rules, generate_post, x_length

VALID_X = "El café de especialidad cuida cada paso, del grano a la taza. #Café"
TOO_LONG_X = "Café " * 70 + "#Café"  # más de 280 caracteres


def test_x_length_counts_emojis_as_two():
    assert x_length("café") == 4
    assert x_length("☕") == 2
    assert x_length("☕️") == 2  # el selector invisible U+FE0F no cuenta


def test_check_rules_accepts_a_valid_x_post():
    assert check_rules(VALID_X, "x") == []


def test_check_rules_rejects_a_long_x_post():
    assert check_rules(TOO_LONG_X, "x") != []


def test_generate_post_without_retry_when_first_answer_is_valid():
    model = FakeListChatModel(responses=[VALID_X])

    result = generate_post("Café de especialidad", "x", "general", model)

    assert result.content == VALID_X
    assert result.warnings == []


def test_generate_post_retries_once_when_rules_fail():
    model = FakeListChatModel(responses=[TOO_LONG_X, VALID_X])

    result = generate_post("Café de especialidad", "x", "general", model)

    assert result.content == VALID_X  # se queda con el segundo intento, que sí cumple
    assert result.warnings == []


def test_generate_post_warns_when_retry_also_fails():
    model = FakeListChatModel(responses=[TOO_LONG_X, TOO_LONG_X])

    result = generate_post("Café de especialidad", "x", "general", model)

    assert result.warnings != []  # devuelve el post, pero avisa