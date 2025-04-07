from application_sdk.clients.sql import AsyncSQLClient
from application_sdk.common.utils import parse_credentials_extra


class PostgreSQLClient(AsyncSQLClient):
    def get_sqlalchemy_connection_string(self) -> str:
        """
        Get the SQLAlchemy connection string for the PostgreSQL client
        based on the auth type and source connection params.

        Returns:
            str: The SQLAlchemy connection string.
        """

        source_connection_params = {
            "application_name": "Atlan",
            "connect_timeout": 5,
        }

        auth_token = self.get_auth_token()

        connection_string = (
            "postgresql+psycopg://{username}:{password}@{host}:{port}/{database}"
        )

        extra = parse_credentials_extra(self.credentials)
        database = extra.get("database")
        connection_string = connection_string.format(
            username=self.credentials["username"],
            password=auth_token,
            host=self.credentials["host"],
            port=self.credentials["port"],
            database=database,
        )

        connection_string = self.add_source_connection_params(
            connection_string, source_connection_params
        )
        return connection_string
