<p align="center">
  <img src="./docs/images/postgres_logo.svg" alt="PostgreSQL Logo" width="200" height="auto">
</p>

# PostgreSQL Application

[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://github.com/atlanhq/atlan-postgres-app/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/atlanhq/atlan-postgres-app/actions/workflows/unit-tests.yml)

PostgreSQL application is designed to interact with a PostgreSQL database and perform actions on it. The application is built using the [Atlan Python Application SDK](https://github.com/atlanhq/application-sdk) and is intended to run on the Atlan Platform.

This application has two components:

- FastAPI server that exposes REST API to interact with the application.
- A workflow that runs on the Atlan platform that extracts metadata from a Postgres database, transforms it and pushes it to an object store.

https://github.com/user-attachments/assets/0ce63557-7c62-4491-96b9-1134a1ceadd6

## Table of contents

- [Usage](#usage)
- [Features](#features)
- [Extending this application to other SQL sources](#extending-this-application-to-other-sql-sources)
- [Development](#development)
- [Architecture](./docs/ARCHITECTURE.md)

## Usage

### Setting up your environment

1. Clone the repository:
   ```bash
   git clone https://github.com/atlanhq/atlan-postgres-app.git
   cd atlan-postgres-app
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

1. Extract metadata from a Postgres database, transform and push to an object store
2. FastAPI-based REST API interface
3. OpenTelemetry integration for metrics, traces and logs
4. IAM Authentication support


### Note on IAM Authentication

This application generates new IAM authentication tokens on-demand for each connection string creation, rather than using SQLAlchemy's refresh token strategy. This approach is chosen because:

1. IAM tokens expire if no connection is created within 15 minutes of token creation
2. Our implementation creates the engine and connection immediately after token generation
3. Connection strings are generated on-demand, ensuring fresh tokens for each new connection

## Extending this application to other SQL sources

1. Make sure you add the required SQLAlchemy dialect using uv. For ex. to add Snowflake dialect, `uv add snowflake-sqlalchemy`
2. Update SQL queries in [`sql`](app/sql) directory
3. Update the DB_CONFIG in the [`app/clients`](app/clients) directory
4. Run the application using the development guide
5. Update the tests in the [`tests`](tests) directory

## Development

- [Development and Quickstart Guide](./docs/DEVELOPMENT.md)
- This application is just an SQL application implementation of Atlan's [Python Application SDK](https://github.com/atlanhq/application-sdk)
  - Please refer to the [examples](https://github.com/atlanhq/application-sdk/tree/main/examples) in the SDK to see how to use the SDK to build different applications on the Atlan Platform.
