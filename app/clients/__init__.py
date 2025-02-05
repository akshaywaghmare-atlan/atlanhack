import os
from urllib.parse import quote_plus

from application_sdk.clients.sql import AsyncSQLClient
from application_sdk.common.aws_utils import (
    generate_aws_rds_token_with_iam_role,
    generate_aws_rds_token_with_iam_user,
)

from utils.utils import parse_credentials_extra


class PostgreSQLClient(AsyncSQLClient):
    source_connection_params = {
        "application_name": "Atlan",
        "connect_timeout": 5,
    }

    def get_iam_user_connection_string(self):
        extra = parse_credentials_extra(self.credentials)
        aws_access_key_id = self.credentials["username"]
        aws_secret_access_key = self.credentials["password"]
        host = self.credentials["host"]
        user = extra.get("username")
        database = extra.get("database")
        if not user:
            raise ValueError("username is required for IAM user authentication")
        if not database:
            raise ValueError("database is required for IAM user authentication")

        port = self.credentials["port"]
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
        extra = parse_credentials_extra(self.credentials)
        aws_role_arn = extra.get("aws_role_arn")
        database = extra.get("database")
        external_id = extra.get("aws_external_id")
        if not aws_role_arn:
            raise ValueError("aws_role_arn is required for IAM role authentication")
        if not database:
            raise ValueError("database is required for IAM role authentication")
        if not external_id:
            raise ValueError("aws_external_id is required for IAM role authentication")
        session_name = os.getenv("AWS_SESSION_NAME", "temp-session")
        username = self.credentials["username"]
        host = self.credentials["host"]
        port = self.credentials.get("port", 5432)
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
        extra = parse_credentials_extra(self.credentials)
        username = self.credentials["username"]
        password = self.credentials["password"]
        host = self.credentials["host"]
        port = self.credentials.get("port", 5432)
        database = extra.get("database")
        if not database:
            raise ValueError("database is required for basic authentication")
        encoded_password: str = quote_plus(password)
        return f"postgresql+psycopg://{username}:{encoded_password}@{host}:{port}/{database}"

    def get_sqlalchemy_connection_string(self) -> str:
        authType = self.credentials.get("authType", "basic")  # Default to basic auth

        connection_string = ""

        match authType:
            case "iam_user":
                connection_string = self.get_iam_user_connection_string()
            case "iam_role":
                connection_string = self.get_iam_role_connection_string()
            case "basic":
                connection_string = self.get_basic_connection_string()
            case _:
                raise ValueError(f"Invalid auth type: {authType}")

        for key, value in self.source_connection_params.items():
            if "?" not in connection_string:
                connection_string += "?"
            else:
                connection_string += "&"
            connection_string += f"{key}={value}"

        return connection_string
