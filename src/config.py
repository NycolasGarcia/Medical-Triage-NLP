"""Configuração central do projeto via variáveis de ambiente."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    model_path: str = "models/current"
    mlflow_tracking_uri: str = "sqlite:///mlflow.db"

    # Caixa 6.9/ADR-0004: "sklearn" (padrão) é o pipeline completo de 6.1-6.4
    # (representação vencedora + calibração + limiar); "onnx" é a variante mais
    # rápida de caixa 6.6, com representação mais simples (sem char n-gramas nem
    # marcação de negação — skl2onnx não converte nenhuma das duas).
    model_backend: Literal["sklearn", "onnx"] = "sklearn"


settings = Settings()
