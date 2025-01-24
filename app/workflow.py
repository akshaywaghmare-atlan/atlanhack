from typing import Any, Dict, Union
from urllib.parse import quote_plus

from application_sdk.activities.metadata_extraction.sql import (
    SQLMetadataExtractionActivities,
)
from application_sdk.clients.sql import AsyncSQLClient
from application_sdk.handlers.sql import SQLHandler
from application_sdk.transformers.atlas import AtlasTransformer
from application_sdk.transformers.atlas.sql import Table
from pyatlan.model import assets

from app.const import (
    COLUMN_EXTRACTION_SQL,
    DATABASE_EXTRACTION_SQL,
    FILTER_METADATA_SQL,
    SCHEMA_EXTRACTION_SQL,
    TABLE_EXTRACTION_SQL,
    TABLES_CHECK_SQL,
)


class PostgreSQLClient(AsyncSQLClient):
    def get_sqlalchemy_connection_string(self) -> str:
        encoded_password: str = quote_plus(self.credentials["password"])
        return f"postgresql+psycopg://{self.credentials['user']}:{encoded_password}@{self.credentials['host']}:{self.credentials['port']}/{self.credentials['database']}"


class PostgresWorkflowHandler(SQLHandler):
    """
    Handler class for Postgres SQL workflows
    """

    metadata_sql = FILTER_METADATA_SQL
    tables_check_sql = TABLES_CHECK_SQL


class PostgresActivities(SQLMetadataExtractionActivities):
    fetch_database_sql = DATABASE_EXTRACTION_SQL
    fetch_schema_sql = SCHEMA_EXTRACTION_SQL
    fetch_table_sql = TABLE_EXTRACTION_SQL
    fetch_column_sql = COLUMN_EXTRACTION_SQL


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
