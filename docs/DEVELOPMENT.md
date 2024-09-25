# Development

### How this works?

- There are 3 main components to this application:
    - **Temporal**: This is the workflow engine that is used to schedule and execute the workflow.
    - **DAPR**: This is application runtime that is used to abstract the underlying infrastructure and provide a set of building blocks for the application. In this case, it is used to abstract the object store, secrets manager and state manager.
    - **Application Server** - This is the application that is used to expose endpoints that are used to trigger the workflow via the frontend, view logs, metrics and traces and much more.


> This guide will walk you through the steps to setup the local development environment and start contributing to the project.

**Table of Contents**
- [Prerequisites](#prerequisites)
    - [Development Tools](#development-tools)
    - [Setting up the local development environment](#setting-up-the-local-development-environment)
- [Using VSCode or Cursor](#development-with-vscode-or-cursor)
- [Using Intellij IDEA](#using-intellij-idea)
- [Add OTel agent during IntelliJ run](#add-otel-agent-during-intellij-run)
- [Advanced Configuration](#advanced-configuration)
- [Changing storage of telemetry data](#changing-storage-of-telemetry-data)


## Prerequisites

### Development Tools
1. Python 3.11 or higher
2. [Poetry](https://python-poetry.org/) for dependency management
3. [Temporal CLI installed](https://docs.temporal.io/docs/cli/) to run Temporal server
4. [DAPR CLI installed](https://docs.dapr.io/getting-started/install-dapr-cli/) to run the PaaS System
    - `dapr init --slim` to initialize the DAPR system locally.


### Setting up the local development environment
1. Install poetry by running `pip install poetry`
2. Run `poetry install` to install the dependencies
> [!NOTE]
> 1. You need to have your SSH private key enabled in the terminal you run the install command or you will see a permission denied error while pulling from the private repositories. If you use HTTP tokens/PAT to authenticate, then run the following:
    ```
    git config --global url."https://".insteadOf "ssh://"
    ```
> 2. It is suggested to use run `poetry config virtualenvs.in-project true` to configure poetry to create the virtual environment in the project directory. This will create a `.venv` directory in the project root.
4. Run `source .venv/bin/activate` to activate the virtual environment
5. Run `pre-commit install` to install the pre-commit hooks
6. Start the platform by running `make start-all`. This will start the Temporal server and the DAPR system.


### Development with VSCode or Cursor
1. Follow the above steps (1-5) to install the dependencies and start the platform.
2. Add the following settings to the `.vscode/launch.json` file
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI Server",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
        },
        {
            "name": "Python: Debug Tests",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/.venv/bin/pytest",
            "args": [
                "-v",
            ],
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            },
        },
        {
            "name": "Python: Instrumented",
            "type": "debugpy",
            "request": "launch",
            "program": "./.venv/bin/opentelemetry-instrument",
            "args": [
                "--traces_exporter",
                "otlp",
                "--metrics_exporter",
                "otlp",
                "--logs_exporter",
                "otlp",
                "--service_name",
                "postgresql-application",
                "python",
                "main.py"
            ],
            "env": {
                "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:8000/telemetry",
                "OTEL_EXPORTER_OTLP_PROTOCOL": "http/protobuf",
                "PYTHONUNBUFFERED": "1",
                "OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED": "true"
            }
        }
    ]
}
```
> This will create a new configuration for running the FastAPI server, running the tests and running the instrumented FastAPI server with OTel agent.
- You can navigate to the Run and Debug section in the IDE to run the configurations of your choice.


### Working with the frontend (Optional)

> While this repository already contains the compiled frontend, if you wish to work on the frontend, you can run the following commands to install the dependencies and build the frontend.

1. Run `cd frontend` to navigate to the frontend directory
2. Run `npm install` to install the dependencies
3. Run `npm run generate` to build the frontend

## Using Intellij IDEA
1. Open the project in Intellij IDEA PyCharm
2. Create a new run configuration for the project
3. Set the script path to `.venv/bin/fastapi`
4. Set the parameters to `dev main.py`
5. The application support auto-reload, so you can make changes to the code and the server will automatically restart


## Add OTel agent during IntelliJ run
1. Create a new run configuration for the project
2. Set the script path to `.venv/bin/opentelemetry-instrument`
3. Set parameters to `--traces_exporter otlp --metrics_exporter otlp --logs_exporter otlp --service_name postgresql-app python main.py`
4. Add environment variable `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:8000/telemetry;OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf;PYTHONUNBUFFERED=1;OTEL_PYTHON_LOGGING_AUTO_INSTRUMENTATION_ENABLED=true`
5. Run the configuration

## Advanced Configuration

### Changing storage of telemetry data
The SDK uses SQLite as the default storage for telemetry data using SQLAlchemy and the SQLite file is stored in `/tmp/app.db`.
You can change the storage to any database with SQLAlchemy compatibility by setting the `SQLALCHEMY_DATABASE_URI` and `SQLALCHEMY_CONNECT_ARGS` environment variables and installing the SQLAlchemy compatible database driver.

