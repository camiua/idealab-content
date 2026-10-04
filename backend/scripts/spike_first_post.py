# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "langchain-ollama",
#     "langchain-groq",
#     "python-dotenv",
# ]
# ///
"""Spike T-1.1: primer post generado con LangChain, usando Ollama (local) y Groq (nube).

Envía el mismo prompt a los dos proveedores y muestra la respuesta, el tiempo y los tokens.
Es un script de exploración: el código definitivo vivirá en backend/app/.

Uso, desde la raíz del repositorio:
    uv run backend/scripts/spike_first_post.py
"""

import os
import sys
import time

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

load_dotenv()
sys.stdout.reconfigure(encoding="utf-8")

MESSAGES = [
    SystemMessage(
        content = (
            "Eres community manager de una cafetería de barrio en Madrid. "
            "Escribes en castellano (español de España)."
        )
    ),
    HumanMessage(
        content = (
            "Escribe un post de Instagram sobre el café de especialidad "
            "para un público joven. Máximo 80 palabras, con emojis "
            "y 3 hashtags al final."
        )
    )
]

def generate(name: str, model) -> None:
    """Envía el prompt a un modelo e imprime la respuesta, el tiempo y los tokens."""
    print(f"\n===== {name} =====")
    
    start = time.perf_counter()
    response = model.invoke(MESSAGES)
    elapsed = time.perf_counter() - start
    
    print(response.content)
    print(f"\n⏱  {elapsed:.1f} s")
    
    usage = response.usage_metadata
    if usage:
        print(f"🔢 {usage['input_tokens']} tokens de entrada · {usage['output_tokens']} de salida")
        
def main() -> None:
    ollama = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.7,
    )
    groq = ChatGroq(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        temperature=0.7,
    )

    generate("Ollama (local)", ollama)
    generate("Groq (nube)", groq)


if __name__ == "__main__":
    main()