"""Schemas Pydantic de entrada/saída da API de triagem."""

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    text: str = Field(min_length=1, description="Texto livre do laudo médico")


class PredictResponse(BaseModel):
    label: str
    probabilities: dict[str, float]
    model_version: str


class HealthResponse(BaseModel):
    status: str = "ok"
