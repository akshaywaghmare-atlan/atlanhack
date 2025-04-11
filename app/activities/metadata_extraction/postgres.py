from typing import Any, Dict

from application_sdk.activities.common.utils import auto_heartbeater
from application_sdk.activities.metadata_extraction.sql import (
    SQLMetadataExtractionActivities,
)
from application_sdk.common.utils import prepare_query
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
    async def fetch_procedures(self, workflow_args: Dict[str, Any]):
        state = await self._get_state(workflow_args)
        sql_input = SQLQueryInput(
            engine=state.sql_client.engine,
            query=prepare_query(
                query=self.fetch_procedure_sql, workflow_args=workflow_args
            ),
            chunk_size=None,
        )
        sql_input = await sql_input.get_daft_dataframe()

        raw_output = ParquetOutput(
            output_prefix=workflow_args.get("output_prefix"),
            output_path=workflow_args.get("output_path"),
            output_suffix="raw/extras-procedure",
        )
        await raw_output.write_daft_dataframe(sql_input)
        return await raw_output.get_statistics(typename="extras-procedure")
