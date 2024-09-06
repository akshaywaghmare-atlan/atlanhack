# Postgres Extraction Application

This application is designed to extract data from a Postgres database and save it to a CSV file. The application is written in Python and uses the `psycopg2` library to connect to the database.

## Building and running the application locally
1. Install poetry by running `pip install poetry`
2. Run `poetry install` to install the dependencies
3. Run `source .venv/bin/activate` to activate the virtual environment
4. Run `fastapi dev main.py` to start the application


### Using Intellij IDEA
1. Open the project in Intellij IDEA PyCharm
2. Create a new run configuration for the project
3. Set the script path to `.venv/bin/fastapi`
4. Set the parameters to `dev main.py`


