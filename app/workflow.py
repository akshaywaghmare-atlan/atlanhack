from typing import Any, Dict
from urllib.parse import quote_plus

from application_sdk.workflows.sql import SQLWorkflowBuilderInterface
from application_sdk.workflows.sql.metadata import SQLWorkflowMetadataInterface
from application_sdk.workflows.sql.preflight_check import (
    SQLWorkflowPreflightCheckInterface,
)
from application_sdk.workflows.sql.workflow import SQLWorkflowWorkerInterface
from temporalio import workflow

from app.const import (
    COLUMN_EXTRACTION_SQL,
    DATABASE_EXTRACTION_SQL,
    FILTER_METADATA_SQL,
    SCHEMA_EXTRACTION_SQL,
    TABLE_EXTRACTION_SQL,
    TABLES_CHECK_SQL,
    TASK_QUEUE_NAME,
)

APPLICATION_NAME = "postgres-connector"


class PostgresWorkflowMetadata(SQLWorkflowMetadataInterface):
    METADATA_SQL = FILTER_METADATA_SQL


class PostgresWorkflowPreflight(SQLWorkflowPreflightCheckInterface):
    METADATA_SQL = FILTER_METADATA_SQL
    TABLES_CHECK_SQL = TABLES_CHECK_SQL


@workflow.defn
class PostgresWorkflowWorker(SQLWorkflowWorkerInterface):
    DATABASE_SQL = DATABASE_EXTRACTION_SQL
    SCHEMA_SQL = SCHEMA_EXTRACTION_SQL
    TABLE_SQL = TABLE_EXTRACTION_SQL
    COLUMN_SQL = COLUMN_EXTRACTION_SQL

    def __init__(
        self, application_name: str = APPLICATION_NAME, *args: Any, **kwargs: Any
    ):
        self.TEMPORAL_WORKFLOW_CLASS = PostgresWorkflowWorker
        super().__init__(application_name, *args, **kwargs)

    @workflow.run
    async def run(self, workflow_args: Dict[str, Any]):
        await super().run(workflow_args)


class PostgresWorkflowBuilder(SQLWorkflowBuilderInterface):
    def get_sqlalchemy_connect_args(
        self, credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {}

    def get_sqlalchemy_connection_string(self, credentials: Dict[str, Any]) -> str:
        encoded_password = quote_plus(credentials["password"])
        return f"postgresql+psycopg2://{credentials['user']}:{encoded_password}@{credentials['host']}:{credentials['port']}/{credentials['database']}"

    def __init__(self, *args: Any, **kwargs: Any):
        self.metadata_interface = PostgresWorkflowMetadata(self.get_sql_engine)
        self.preflight_interface = PostgresWorkflowPreflight(self.get_sql_engine)
        self.worker_interface = PostgresWorkflowWorker(
            APPLICATION_NAME, get_sql_engine=self.get_sql_engine
        )
        super().__init__(
            metadata_interface=self.metadata_interface,
            preflight_check_interface=self.preflight_interface,
            worker_interface=self.worker_interface,
            *args,
            **kwargs,
        )
