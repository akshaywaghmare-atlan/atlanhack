# Postgres Extraction Application

This application is designed to extract metadata from a Postgres database and save it to an object store. The application is written in Python and uses the `psycopg2` library to connect to the database.

[![Checked with pyright](https://microsoft.github.io/pyright/img/pyright_badge.svg)](https://microsoft.github.io/pyright/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Tests](https://github.com/atlanhq/phoenix-postgres-app/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/atlanhq/phoenix-postgres-app/actions/workflows/unit-tests.yml)

### Demo

https://github.com/user-attachments/assets/6f529307-3d2e-405b-ae66-311e712b920f

### Clone the repository

To clone this repository including the submodule, use the following command:

```bash
git clone --recurse-submodules https://github.com/atlanhq/phoenix-postgres-app.git
```

### Development
- [Development and Quickstart Guide](./docs/DEVELOPMENT.md)
- This application is just an SQL application implementation of Atlan's [Python Application SDK](https://github.com/atlanhq/application-sdk)
  - Please refer to the [examples](https://github.com/atlanhq/application-sdk/tree/main/examples) in the SDK to see how to use the SDK to build different applications on the Atlan Platform


### Contributing
- Slack - #collab-phoenix