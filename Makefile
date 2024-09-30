# Define variables
APP_NAME := phoenix-postgres-app

# Phony targets
.PHONY: run start-dapr start-temporal-dev start-all

# Run Temporal locally
start-temporal-dev:
	temporal server start-dev

start-dapr:
	dapr run --app-id app --app-port 3000 --dapr-http-port 3500 --dapr-grpc-port 50001 --dapr-http-max-request-size 1024 --resources-path .venv/src/application-sdk/components

start-all:
	make start-dapr & make start-temporal-dev

install:
    poetry install
    source .venv/bin/activate
    pre-commit install

# Run the application
run:
    source .venv/bin/activate
    export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:8000/telemetry"
    export OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
    export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
    export OTEL_PYTHON_EXCLUDED_URLS="/telemetry/.*,/system/.*"
    ./.venv/bin/opentelemetry-instrument --traces_exporter otlp --metrics_exporter otlp --logs_exporter otlp --service_name postgresql-application python main.py