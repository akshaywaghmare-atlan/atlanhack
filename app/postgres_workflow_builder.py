from sdk.workflows.sql import SQLWorkflowBuilderInterface
from typing import Dict, Any


class PostgresWorkflowBuilder(SQLWorkflowBuilderInterface):
    def get_sqlalchemy_connection_string(self, credentials: Dict[str, Any]) -> str:
        return f"postgresql+psycopg2://{credentials['username']}:{credentials['password']}@{credentials['host']}:{credentials['port']}/{credentials['database']}"

    def get_sqlalchemy_connect_args(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        return {}