from application_sdk.workflows.sql.builders.builder import SQLWorkflowBuilder
from application_sdk.workflows.sql.controllers.metadata import (
    SQLWorkflowMetadataController,
)
from application_sdk.workflows.sql.controllers.preflight_check import (
    SQLWorkflowPreflightCheckController,
)
from application_sdk.workflows.sql.workflows.workflow import SQLWorkflow
from application_sdk.workflows.transformers.phoenix import PhoenixTransformer

from app.const import (
    COLUMN_EXTRACTION_SQL,
    DATABASE_EXTRACTION_SQL,
    FILTER_METADATA_SQL,
    SCHEMA_EXTRACTION_SQL,
    TABLE_EXTRACTION_SQL,
    TABLES_CHECK_SQL,
)

APPLICATION_NAME = "postgres-connector"


class PostgresWorkflowMetadata(SQLWorkflowMetadataController):
    METADATA_SQL = FILTER_METADATA_SQL


class PostgresWorkflowPreflight(SQLWorkflowPreflightCheckController):
    METADATA_SQL = FILTER_METADATA_SQL
    TABLES_CHECK_SQL = TABLES_CHECK_SQL


class PostgresWorkflow(SQLWorkflow):
    fetch_database_sql = DATABASE_EXTRACTION_SQL
    fetch_schema_sql = SCHEMA_EXTRACTION_SQL
    fetch_table_sql = TABLE_EXTRACTION_SQL
    fetch_column_sql = COLUMN_EXTRACTION_SQL


class PostgresWorkflowBuilder(SQLWorkflowBuilder):
    def __init__(self, application_name: str = APPLICATION_NAME):
        self.set_transformer(
            PhoenixTransformer(
                connector_name=application_name, connector_type="postgres"
            )
        )

        super().__init__()

    def build(self, workflow: SQLWorkflow | None = None) -> SQLWorkflow:
        return super().build(workflow=workflow or PostgresWorkflow())
