FROM python:3.12-slim

# uv, copied from its official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# LightGBM needs the OpenMP runtime
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Dependencies first: this layer is cached until the lockfile changes
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# Then the application code and the model files
COPY . .

ENV PATH="/app/.venv/bin:$PATH" \
    MODEL_DIR=/app/artifacts \
    PYTHONUNBUFFERED=1

RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
