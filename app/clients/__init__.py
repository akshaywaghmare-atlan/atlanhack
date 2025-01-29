from urllib.parse import quote_plus

from application_sdk.clients.sql import AsyncSQLClient
from application_sdk.common.aws_utils import (
    generate_aws_rds_token_with_iam_role,
    generate_aws_rds_token_with_iam_user,
)


class PostgreSQLClient(AsyncSQLClient):
    def get_iam_user_connection_string(self):
        token = quote_plus(
            generate_aws_rds_token_with_iam_user(
                self.credentials["access_key_id"],
                self.credentials["secret_access_key"],
                self.credentials["host"],
                self.credentials["username"],
                self.credentials["port"],
            )
        )
        return f"postgresql+psycopg://{self.credentials['username']}:{token}@{self.credentials['host']}:{self.credentials['port']}/{self.credentials['database']}"

    def get_iam_role_connection_string(self):
        token = quote_plus(
            generate_aws_rds_token_with_iam_role(
                role_arn=self.credentials["role_arn"],
                host=self.credentials["host"],
                user=self.credentials["username"],
                external_id=self.credentials.get("external_id"),
                session_name=self.credentials.get("session_name", "temp-session"),
                port=self.credentials.get("port", 5432),
            )
        )
        return f"postgresql+psycopg://{self.credentials['username']}:{token}@{self.credentials['host']}:{self.credentials['port']}/{self.credentials['database']}"

    def get_basic_connection_string(self):
        encoded_password: str = quote_plus(self.credentials["password"])
        return f"postgresql+psycopg://{self.credentials['username']}:{encoded_password}@{self.credentials['host']}:{self.credentials['port']}/{self.credentials['database']}"

    def get_sqlalchemy_connection_string(self) -> str:
        authType = self.credentials.get("authType", "basic")  # Default to basic auth

        match authType:
            case "iam_user":
                return self.get_iam_user_connection_string()
            case "iam_role":
                return self.get_iam_role_connection_string()
            case "basic":
                return self.get_basic_connection_string()
            case _:
                raise ValueError(f"Invalid auth type: {authType}")
