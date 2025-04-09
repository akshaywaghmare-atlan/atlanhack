from application_sdk.activities.common.utils import auto_heartbeater
from application_sdk.activities.metadata_extraction.sql import (
    SQLMetadataExtractionActivities,
)
from application_sdk.decorators import transform_daft
from application_sdk.inputs.sql_query import SQLQueryInput
from application_sdk.outputs.parquet import ParquetOutput
from temporalio import activity

from app.const import (
    COLUMN_EXTRACTION_SQL,
    COLUMN_EXTRACTION_TEMP_TABLE_REGEX_SQL,
    DATABASE_EXTRACTION_SQL,
    PROCEDURE_EXTRACTION_SQL,
    SCHEMA_EXTRACTION_SQL,
    TABLE_EXTRACTION_SQL,
    TABLE_EXTRACTION_TEMP_TABLE_REGEX_SQL,
)


class PostgresMetadataExtractionActivities(SQLMetadataExtractionActivities):
    fetch_database_sql = DATABASE_EXTRACTION_SQL
    fetch_schema_sql = SCHEMA_EXTRACTION_SQL
    fetch_table_sql = TABLE_EXTRACTION_SQL
    fetch_column_sql = COLUMN_EXTRACTION_SQL
    fetch_procedure_sql = PROCEDURE_EXTRACTION_SQL

    tables_extraction_temp_table_regex_sql = TABLE_EXTRACTION_TEMP_TABLE_REGEX_SQL
    column_extraction_temp_table_regex_sql = COLUMN_EXTRACTION_TEMP_TABLE_REGEX_SQL

    @activity.defn
    @auto_heartbeater
    @transform_daft(
        batch_input=SQLQueryInput(query="fetch_procedure_sql", chunk_size=None),
        raw_output=ParquetOutput(output_suffix="/raw/extras-procedure"),
    )
    async def fetch_procedures(self, batch_input, raw_output: ParquetOutput, **kwargs):
        await raw_output.write_daft_dataframe(batch_input)
        return await raw_output.get_statistics(typename="extras-procedure")
