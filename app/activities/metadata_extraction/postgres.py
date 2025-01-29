from application_sdk.activities.metadata_extraction.sql import (
    SQLMetadataExtractionActivities,
)

from app.const import (
    COLUMN_EXTRACTION_SQL,
    COLUMN_EXTRACTION_TEMP_TABLE_REGEX_SQL,
    DATABASE_EXTRACTION_SQL,
    SCHEMA_EXTRACTION_SQL,
    TABLE_EXTRACTION_SQL,
    TABLE_EXTRACTION_TEMP_TABLE_REGEX_SQL,
)


class PostgresActivities(SQLMetadataExtractionActivities):
    fetch_database_sql = DATABASE_EXTRACTION_SQL
    fetch_schema_sql = SCHEMA_EXTRACTION_SQL
    fetch_table_sql = TABLE_EXTRACTION_SQL
    fetch_column_sql = COLUMN_EXTRACTION_SQL

    tables_extraction_temp_table_regex_sql = TABLE_EXTRACTION_TEMP_TABLE_REGEX_SQL
    column_extraction_temp_table_regex_sql = COLUMN_EXTRACTION_TEMP_TABLE_REGEX_SQL
