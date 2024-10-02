<p align="center">
  <img src="./docs/images/postgres_logo.svg" alt="PostgreSQL Logo" width="200" height="auto">
</p>

# PostgreSQL Application


This application is designed to interact with a PostgreSQL database and perform actions on it. The application is built using the [Atlan Python Application SDK](https://github.com/atlanhq/application-sdk) and is intended to run on the Atlan Platform.

**Overview:**
- The application is a FastAPI application.
- It also houses a workflow that extracts metadata from a Postgres database, transforms it and pushes it to an object store.

[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://github.com/atlanhq/phoenix-postgres-app/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/atlanhq/phoenix-postgres-app/actions/workflows/unit-tests.yml)

## Table of contents
- [Features](#features)
- [Extending this application to other SQL sources](#extending-this-application-to-other-sql-sources)
- [Demo](#demo)
- [Development](#development)
- [Architecture](./docs/ARCHITECTURE.md)

## Features
1. Extract metadata from a Postgres database, transform and push to an object store
2. Supports Adhoc SQL queries on Postgres
3. OTel integration for metrics, traces and logs
4. _(In development)Supports mining query history from Postgres_
5. _(In development)Supports metadata(including tag) sync between Atlan and Postgres_
6. _(In development)Supports data profiling on Postgres_
7. _(In development)Supports data quality checks on Postgres_
8. _(In development)Supports data lineage on Postgres_


## Extending this application to other SQL sources
1. Make sure you add the required SQLAlchemy dialect using poetry. For ex. to add Snowflake dialect, `poetry add snowflake-sqlalchemy`
2. Update SQL queries in [`const.py`](app/const.py) file
3. Update the SQLAlchemy connection string generation in the [`workflow.py`](app/workflow.py) file
4. Run the application using the development guide
5. Update the tests in the [`tests`](tests) directory

## Demo

https://github.com/user-attachments/assets/6f529307-3d2e-405b-ae66-311e712b920f

## Development
- Setup the local development environment on [Mac](./docs/SETUP_MAC.md)
- [Development and Quickstart Guide](./docs/DEVELOPMENT.md)
- This application is just an SQL application implementation of Atlan's [Python Application SDK](https://github.com/atlanhq/application-sdk)
  - Please refer to the [examples](https://github.com/atlanhq/application-sdk/tree/main/examples) in the SDK to see how to use the SDK to build different applications on the Atlan Platform.
