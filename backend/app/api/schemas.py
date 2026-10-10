"""Contratos de entrada y salida de la API (spec §1.3)."""

from pydantic import BaseModel, Field

from app.config import Provider
from app.prompts.builder import Audience, Platform


class GenerateRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=200, examples=["Café de especialidad"])
    platform: Platform 
    audience: Audience
    provider: Provider | None = None
    

class Metrics(BaseModel):
    elapsed_ms: int
    
    
class GenerateResponse(BaseModel):
    content: str
    platform: Platform
    provider: Provider
    model: str
    metrics: Metrics
    warnings: list[str]
    prompt_versions: dict[str, str]
    
