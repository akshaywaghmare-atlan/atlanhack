from application_sdk.handlers.sql import SQLHandler

from app.const import FILTER_METADATA_SQL, TABLES_CHECK_SQL


class PostgresWorkflowHandler(SQLHandler):
    """
    Handler class for Postgres SQL workflows
    """

    metadata_sql = FILTER_METADATA_SQL
    tables_check_sql = TABLES_CHECK_SQL
