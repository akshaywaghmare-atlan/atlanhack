from application_sdk.handlers.sql import SQLHandler

from app.const import (
    FILTER_METADATA_SQL,
    GET_CLIENT_VERSION_SQL,
    TABLES_CHECK_SQL,
    TABLES_CHECK_TEMP_TABLE_REGEX_SQL,
)


class PostgresWorkflowHandler(SQLHandler):
    """
    Handler class for Postgres SQL workflows
    Primarily handles business logic for test authentication, preflight checks and more.
    """

    metadata_sql = FILTER_METADATA_SQL
    tables_check_sql = TABLES_CHECK_SQL
    temp_table_regex_sql = TABLES_CHECK_TEMP_TABLE_REGEX_SQL
    get_client_version_sql = GET_CLIENT_VERSION_SQL
