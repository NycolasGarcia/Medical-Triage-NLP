FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.10 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src/ src/
COPY models/ models/


FROM python:3.11-slim AS runtime

# libgomp1: onnxruntime (caixa 6.6) usa OpenMP para paralelismo interno em runtime.
# locales: o operador StringNormalizer do onnxruntime (parte do TfidfVectorizer
# exportado) falha na inicialização sem um locale UTF-8 disponível — a imagem slim
# não vem com nenhum instalado; achado real ao testar o backend ONNX em container
# (não aparecia rodando local fora de container, onde o locale do host já existe).
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 locales \
    && sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8

RUN useradd --create-home --shell /usr/sbin/nologin appuser
WORKDIR /app
COPY --from=builder --chown=appuser:appuser /app /app
ENV PATH="/app/.venv/bin:$PATH"

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=2)" || exit 1

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
