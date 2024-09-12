from sdk.workflows.sql import SQLWorkflowBuilderInterface, SQLWorkflowMetadataInterface
from typing import Dict, Any

from sdk.workflows.sql.preflight_check import SQLWorkflowPreflightCheckInterface


class PostgresMetadataWorkflow(SQLWorkflowMetadataInterface):
    METADATA_SQL = """
        SELECT
            CATALOG_NAME as DATABASE_NAME,
            SCHEMA_NAME as SCHEMA_NAME
        FROM INFORMATION_SCHEMA.SCHEMATA
    """


class PostgresWorkflowBuilder(SQLWorkflowBuilderInterface):
    def get_sqlalchemy_connection_string(self, credentials: Dict[str, Any]) -> str:
        return f"postgresql+psycopg2://{credentials['username']}:{credentials['password']}@{credentials['host']}:{credentials['port']}/{credentials['database']}"

    def get_sqlalchemy_connect_args(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        return {}

    def __init__(self):
        preflight_check = SQLWorkflowPreflightCheckInterface(
            self.get_sqlalchemy_connection_string,
            self.get_sqlalchemy_connect_args,
        )
        preflight_check.METADATA_SQL = PostgresMetadataWorkflow.METADATA_SQL
        metadata_interface = PostgresMetadataWorkflow(
            self.get_sqlalchemy_connection_string,
            self.get_sqlalchemy_connect_args,
        )
        super().__init__(
            metadata_interface=metadata_interface,
            preflight_check_interface=preflight_check,
        )

