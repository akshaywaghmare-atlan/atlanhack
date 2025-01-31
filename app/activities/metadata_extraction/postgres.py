import pandas as pd
from application_sdk.activities.common.utils import auto_heartbeater
from application_sdk.activities.metadata_extraction.sql import (
    SQLMetadataExtractionActivities,
)
from application_sdk.decorators import transform
from application_sdk.inputs.sql_query import SQLQueryInput
from application_sdk.outputs.json import JsonOutput
from temporalio import activity

from app.clients import PostgreSQLClient
from app.const import (
    COLUMN_EXTRACTION_SQL,
    COLUMN_EXTRACTION_TEMP_TABLE_REGEX_SQL,
    DATABASE_EXTRACTION_SQL,
    PROCEDURE_EXTRACTION_SQL,
    SCHEMA_EXTRACTION_SQL,
    TABLE_EXTRACTION_SQL,
    TABLE_EXTRACTION_TEMP_TABLE_REGEX_SQL,
)
from app.handlers import PostgresWorkflowHandler
from app.transformers.atlas import PostgresAtlasTransformer


class PostgresMetadataExtractionActivities(SQLMetadataExtractionActivities):
    fetch_database_sql = DATABASE_EXTRACTION_SQL
    fetch_schema_sql = SCHEMA_EXTRACTION_SQL
    fetch_table_sql = TABLE_EXTRACTION_SQL
    fetch_column_sql = COLUMN_EXTRACTION_SQL
    fetch_procedure_sql = PROCEDURE_EXTRACTION_SQL

    tables_extraction_temp_table_regex_sql = TABLE_EXTRACTION_TEMP_TABLE_REGEX_SQL
    column_extraction_temp_table_regex_sql = COLUMN_EXTRACTION_TEMP_TABLE_REGEX_SQL

    sql_client_class = PostgreSQLClient
    handler_class = PostgresWorkflowHandler
    transformer_class = PostgresAtlasTransformer

    @activity.defn
    @auto_heartbeater
    @transform(
        batch_input=SQLQueryInput(query="fetch_procedure_sql"),
        raw_output=JsonOutput(output_suffix="/raw/extra-procedure"),
    )
    async def fetch_procedures(
        self, batch_input: pd.DataFrame, raw_output: JsonOutput, **kwargs
    ):
        await raw_output.write_batched_dataframe(batch_input)
        return raw_output.get_metadata(typename="extra-procedure")
