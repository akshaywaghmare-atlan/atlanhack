from sdk.workflows import WorkflowWorkerInterface


class SQLWorkflowWorkerInterface(WorkflowWorkerInterface):

    DATABASE_SQL = ""
    SCHEMA_SQL = ""
    TABLE_SQL = ""
    COLUMN_SQL = ""

    def __init__(self,
                 get_sql_alchemy_string_fn,
                 get_sql_alchemy_connect_args_fn):
        self.get_sql_alchemy_string_fn = get_sql_alchemy_string_fn
        self.get_sql_alchemy_connect_args_fn = get_sql_alchemy_connect_args_fn


    def run(self):
        raise NotImplementedError

    def fetch_databases(self):
        raise NotImplementedError


    def fetch_schemas(self, database):
        raise NotImplementedError

    def fetch_tables(self, database):
        raise NotImplementedError

    def fetch_columns(self, database, schema, table):
        raise NotImplementedError

    def fetch_from_sql(self, database, sql):
        raise NotImplementedError