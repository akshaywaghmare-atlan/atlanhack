# Postgres Extraction Application

This application is designed to extract data from a Postgres database and save it to a CSV file. The application is written in Python and uses the `psycopg2` library to connect to the database.


### Clone the repository

To clone this repository including the submodule, use the following command:

```bash
git clone --recurse-submodules https://github.com/atlanhq/postgres-extraction-app.git
```


### Building and running the application locally
1. Install poetry by running `pip install poetry`
2. Run `poetry install` to install the dependencies
> [!NOTE]
> It is suggested to use run `poetry config virtualenvs.in-project true` to configure poetry to create the virtual environment in the project directory. This will create a `.venv` directory in the project root.
3. Run `source .venv/bin/activate` to activate the virtual environment
4. Run `fastapi dev main.py` to start the application


### Using Intellij IDEA
1. Open the project in Intellij IDEA PyCharm
2. Create a new run configuration for the project
3. Set the script path to `.venv/bin/fastapi`
4. Set the parameters to `dev main.py`
5. The application support auto-reload, so you can make changes to the code and the server will automatically restart

### Add OTel agent during IntelliJ run
1. Create a new run configuration for the project
2. Set the script path to `.venv/bin/opentelemetry-instrument`
3. Set parameters to `--traces_exporter console,otlp --metrics_exporter console,otlp --logs_exporter console,otlp --service_name your-service-name python main.py`
4. Add environment variable `OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:8000/telemetry;OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf`
5. Run the configuration