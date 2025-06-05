# Atlan Trino App

This application is built using the Atlan Application SDK to extract metadata from Trino databases.

## Prerequisites

1. Python 3.11.10 or higher
2. uv 0.7.3 or higher

## Setup

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd atlan-trino-app
   ```

2. Follow the setup instructions for your platform:
   - [Automatic Setup](./.cursor/rules/setup.mdc) - Automatically detects your OS and provides the appropriate guide
   - [macOS Setup Guide](https://github.com/atlanhq/application-sdk/blob/main/docs/docs/setup/MAC.md)
   - [Linux Setup Guide](https://github.com/atlanhq/application-sdk/blob/main/docs/docs/setup/LINUX.md)
   - [Windows Setup Guide](https://github.com/atlanhq/application-sdk/blob/main/docs/docs/setup/WINDOWS.md)

3. Install dependencies:
   ```bash
   uv sync --all-groups
   ```

3. Download required components:
   ```bash
   uv run poe download-components
   ```

4. Start the dependencies (in a separate terminal):
   ```bash
   uv run poe start-deps
   ```

5. That loads all required dependencies. To run, you just run the command in the main terminal:
   ```bash
   uv run main.py
   ```

## Component Structure

- `app/clients`: Database client implementations
- `app/transformers`: Metadata transformation logic (refer [RDBMS models](https://developer.atlan.com/models/rdbms/))
- `app/sql`: SQL query templates

## Features

1. Extract metadata from a Trino database, transform and push to an object store
2. FastAPI-based REST API interface
3. OpenTelemetry integration for metrics, traces and logs

## Configuration

The application requires the following environment variables:

- `TRINO_HOST`: Trino server host (default: localhost)
- `TRINO_PORT`: Trino server port (default: 8081)
- `TRINO_USER`: Trino username (default: admin)
- `TRINO_CATALOG`: Trino catalog name (default: system)
- `TRINO_SCHEMA`: Trino schema name (default: information_schema)

## Extending this application to other SQL sources

1. Make sure you add the required SQLAlchemy dialect using uv. For ex. to add Snowflake dialect, `uv add snowflake-sqlalchemy`
