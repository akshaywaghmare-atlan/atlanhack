FROM python:3.11-buster as builder

RUN pip install poetry==1.4.2

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install poetry

RUN poetry install --without dev --without test --no-root && rm -rf $POETRY_CACHE_DIR

# Install Python dependencies
COPY ./pyproject.toml ./poetry.lock ./
# the cache directory makes rebuilding a docker image if pyproject.toml changes near instant
RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --no-root --without dev,test --no-interaction --no-ansi

# removing poetry alone saves 200 mb
FROM python:3.11-slim-buster as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

# Copy the rest of the code
COPY . .

ENTRYPOINT ["./.venv/bin/opentelemetry-instrument", "--traces_exporter", "otlp", "--metrics_exporter", "otlp", "--logs_exporter", "otlp", "--service_name", "postgresql-application", "python", "main.py"]
