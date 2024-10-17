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
	# Configure git to use https instead of ssh or git
	@if git ls-remote git@github.com:atlanhq/application-sdk.git > /dev/null 2>&1; then \
		echo "Git is configured to use SSH Protocol"; \
	elif git ls-remote https://github.com/atlanhq/application-sdk.git > /dev/null 2>&1; then \
		echo "Git is configured to use HTTPS Protocol. Configuring to use HTTPS instead..."; \
		git config --global url."https://github.com/".insteadOf "git@github.com:"; \
	else \
		echo "Git is not configured to use SSH or Git Protocol. Please configure Git to use SSH or Git Protocol."; \
		exit 1; \
	fi
	# Configure poetry to use project-specific virtualenv
	poetry config virtualenvs.in-project true

	# Install the dependencies
	poetry install -vv
	poetry update application-sdk --dry-run

	# Activate the virtual environment and install pre-commit hooks
	poetry run pre-commit install

# Run the application
run:
	OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:8000/telemetry" \
	OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf" \
	OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true \
	OTEL_PYTHON_EXCLUDED_URLS="/telemetry/.*,/system/.*" \
	poetry run ./.venv/bin/opentelemetry-instrument --traces_exporter otlp --metrics_exporter otlp --logs_exporter otlp --service_name postgresql-application python main.py
