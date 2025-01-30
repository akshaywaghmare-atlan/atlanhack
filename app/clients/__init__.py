import os
from urllib.parse import quote_plus

from application_sdk.clients.sql import AsyncSQLClient
from application_sdk.common.aws_utils import (
    generate_aws_rds_token_with_iam_role,
    generate_aws_rds_token_with_iam_user,
)


class PostgreSQLClient(AsyncSQLClient):
    def get_iam_user_connection_string(self):
        aws_access_key_id = self.credentials["username"]
        aws_secret_access_key = self.credentials["password"]
        host = self.credentials["host"]
        user = self.credentials.get("extra", {}).get("username")
        port = self.credentials["port"]
        database = self.credentials.get("extra", {}).get("database")
        region = self.credentials.get("region", None)
        token = quote_plus(
            generate_aws_rds_token_with_iam_user(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                host=host,
                user=user,
                port=port,
                region=region,
            )
        )

        return f"postgresql+psycopg://{user}:{token}@{host}:{port}/{database}"

    def get_iam_role_connection_string(self):
        aws_role_arn = self.credentials.get("extra", {}).get("aws_role_arn")
        external_id = self.credentials.get("extra", {}).get("aws_external_id")
        session_name = os.getenv("AWS_SESSION_NAME", "temp-session")
        username = self.credentials["username"]
        host = self.credentials["host"]
        port = self.credentials.get("port", 5432)
        database = self.credentials.get("extra", {}).get("database")
        region = self.credentials.get("region", None)
        token = quote_plus(
            generate_aws_rds_token_with_iam_role(
                role_arn=aws_role_arn,
                host=host,
                user=username,
                external_id=external_id,
                session_name=session_name,
                port=port,
                region=region,
            )
        )
        return f"postgresql+psycopg://{username}:{token}@{host}:{port}/{database}"

    def get_basic_connection_string(self):
        username = self.credentials["username"]
        password = self.credentials["password"]
        host = self.credentials["host"]
        port = self.credentials.get("port", 5432)
        database = self.credentials.get("extra", {}).get("database")
        encoded_password: str = quote_plus(password)
        return f"postgresql+psycopg://{username}:{encoded_password}@{host}:{port}/{database}"

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
