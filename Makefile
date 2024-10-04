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
	@if git ls-remote ssh://github.com/atlanhq/application-sdk.git > /dev/null 2>&1; then \
		echo "Git is configured to use SSH Protocol. Configuring to use HTTPS instead..."; \
		git config --global url."https://".insteadOf "ssh://"; \
	elif git ls-remote git://github.com/atlanhq/application-sdk.git > /dev/null 2>&1; then \
		echo "Git is configured to use Git Protocol. Configuring to use HTTPS instead..."; \
		git config --global url."https://".insteadOf "git://"; \
	else \
		echo "Git is not configured to use SSH or Git Protocol. Please configure Git to use SSH or Git Protocol."; \
		exit 1; \
	fi

	# Configure poetry to use project-specific virtualenv
	poetry config virtualenvs.in-project true

	# Install the dependencies
	poetry install -vv

	# Activate the virtual environment and install pre-commit hooks
	# . .venv/bin/activate && pre-commit install

# Run the application
run:
	export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:8000/telemetry"
	export OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
	export OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true
	export OTEL_PYTHON_EXCLUDED_URLS="/telemetry/.*,/system/.*"
	. .venv/bin/activate && ./.venv/bin/opentelemetry-instrument --traces_exporter otlp --metrics_exporter otlp --logs_exporter otlp --service_name postgresql-application python main.py
