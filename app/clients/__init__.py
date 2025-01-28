from urllib.parse import quote_plus

from application_sdk.clients.sql import AsyncSQLClient


class PostgreSQLClient(AsyncSQLClient):
    def get_sqlalchemy_connection_string(self) -> str:
        encoded_password: str = quote_plus(self.credentials["password"])
        return f"postgresql+psycopg://{self.credentials['user']}:{encoded_password}@{self.credentials['host']}:{self.credentials['port']}/{self.credentials['database']}"
