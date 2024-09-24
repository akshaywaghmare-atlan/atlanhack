import logging
from typing import Any, Dict

from sqlalchemy import create_engine, text

from sdk.workflows import WorkflowPreflightCheckInterface
from sdk.workflows.sql.utils import rows_as_dicts

logger = logging.getLogger(__name__)


class SQLWorkflowPreflightCheckInterface(WorkflowPreflightCheckInterface):
    METADATA_SQL = ""

    def preflight_check(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        credential = form_data.get("credential")
        try:
            engine = create_engine(
                self.get_sql_alchemy_string_fn(credential),
                connect_args=self.get_sql_alchemy_connect_args_fn(credential),
                pool_pre_ping=True,
            )
            with engine.connect() as connection:
                cursor = connection.execute(text(self.METADATA_SQL)).cursor
                # Check if return values are as expected
                metadata = rows_as_dicts(cursor)
                return {"status": "success", "metadata": metadata}
        except Exception as e:
            logger.error(f"Failed to fetch metadata: {str(e)}")
            raise e
