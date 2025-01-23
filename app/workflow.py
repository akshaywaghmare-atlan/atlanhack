import os
from typing import Any, Dict, Union, cast
from urllib.parse import quote_plus

from application_sdk.workflows.controllers import (
    WorkflowPreflightCheckControllerInterface,
)
from application_sdk.workflows.sql.builders.builder import SQLWorkflowBuilder
from application_sdk.workflows.sql.controllers.metadata import (
    SQLWorkflowMetadataController,
)
from application_sdk.workflows.sql.controllers.preflight_check import (
    SQLWorkflowPreflightCheckController,
)
from application_sdk.workflows.sql.resources.async_sql_resource import AsyncSQLResource
from application_sdk.workflows.sql.resources.sql_resource import (
    SQLResource,
    SQLResourceConfig,
)
from application_sdk.workflows.sql.workflows.workflow import SQLWorkflow
from application_sdk.workflows.transformers.atlas import AtlasTransformer
from application_sdk.workflows.transformers.atlas.sql import Table
from pyatlan.model import assets

from app.const import (
    COLUMN_EXTRACTION_SQL,
    DATABASE_EXTRACTION_SQL,
    FILTER_METADATA_SQL,
    SCHEMA_EXTRACTION_SQL,
    TABLE_EXTRACTION_SQL,
    TABLES_CHECK_SQL,
)

APPLICATION_NAME = os.getenv("ATLAN_APPLICATION_NAME", "postgres")
TENANT_ID = os.getenv("ATLAN_TENANT_ID", "development")


class PostgreSQLResource(AsyncSQLResource):
    def get_sqlalchemy_connection_string(self) -> str:
        encoded_password: str = quote_plus(self.config.credentials["password"])
        return f"postgresql+psycopg://{self.config.credentials['user']}:{encoded_password}@{self.config.credentials['host']}:{self.config.credentials['port']}/{self.config.credentials['database']}"


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

    sql_resource: SQLResource | None = PostgreSQLResource(SQLResourceConfig())


class PostgresTable(Table):
    @classmethod
    def parse_obj(
        cls, obj: Dict[str, Any]
    ) -> Union[
        assets.Table, assets.View, assets.MaterialisedView, assets.SnowflakeDynamicTable
    ]:
        """
        Postgres view and materialized view definitions are select queries,
        so we need to format the view definition to be a valid SQL query.

        src: https://github.com/atlanhq/marketplace-packages/blob/master/packages/atlan/postgres/transformers/view.jinja2
        """
        if obj.get("table_type") == "VIEW":
            view_definition = "CREATE OR REPLACE VIEW {view_name} AS {query}"
            obj["view_definition"] = view_definition.format(
                view_name=obj["table_name"], query=obj["view_definition"]
            )
        elif obj.get("table_type") == "MATERIALIZED VIEW":
            view_definition = (
                "CREATE OR REPLACE MATERIALIZED VIEW {view_name} AS {query}"
            )
            obj["view_definition"] = view_definition.format(
                view_name=obj["table_name"], query=obj["view_definition"]
            )

        return super().parse_obj(obj)


class CustomTransformer(AtlasTransformer):
    def __init__(self, connector_name: str, tenant_id: str, **kwargs: Any):
        super().__init__(connector_name, tenant_id, **kwargs)

        self.entity_class_definitions["TABLE"] = PostgresTable
        self.entity_class_definitions["VIEW"] = PostgresTable
        self.entity_class_definitions["MATERIALIZED VIEW"] = PostgresTable


class PostgresWorkflowBuilder(SQLWorkflowBuilder):
    preflight_check_controller: WorkflowPreflightCheckControllerInterface

    def __init__(self, application_name: str = APPLICATION_NAME):
        self.set_transformer(
            CustomTransformer(
                connector_name=application_name,
                connector_type="postgres",
                tenant_id=TENANT_ID,
            )
        )

        super().__init__()

    def build(self, workflow: SQLWorkflow | None = None) -> SQLWorkflow:
        workflow = workflow or PostgresWorkflow()
        workflow = (  # type: ignore
            workflow.set_sql_resource(self.sql_resource)
            .set_transformer(self.transformer)
            .set_temporal_resource(self.temporal_resource)
            .set_preflight_check_controller(
                PostgresWorkflowPreflight(sql_resource=self.sql_resource)
            )
        )

        return cast(SQLWorkflow, workflow)
