# Install uv
FROM python:3.11-slim

# Install git (and optionally build-essential if you have other build dependencies)
# Note: this is required for uv's git-based dependency resolution to work
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Change the working directory to the `app` directory
WORKDIR /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=README.md,target=README.md \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml

# Copy the project into the image
ADD . /app

# Sync the project
RUN uv venv .venv
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --extra dev --locked --no-install-project

# Set the entrypoint
ENTRYPOINT ["python", "/app/main.py"]