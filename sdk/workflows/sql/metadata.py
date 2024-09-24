import logging
from typing import Any, Dict, List

from sqlalchemy import create_engine, text

from sdk.workflows import WorkflowMetadataInterface
from sdk.workflows.sql.utils import rows_as_dicts

logger = logging.getLogger(__name__)


class SQLWorkflowMetadataInterface(WorkflowMetadataInterface):
    METADATA_SQL = ""

    def fetch_metadata(self, credential: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            engine = create_engine(
                self.get_sql_alchemy_string_fn(credential),
                connect_args=self.get_sql_alchemy_connect_args_fn(credential),
                pool_pre_ping=True,
            )
            with engine.connect() as connection:
                cursor = connection.execute(text(self.METADATA_SQL)).cursor
                return rows_as_dicts(cursor)
        except Exception as e:
            logger.error(f"Failed to fetch metadata: {str(e)}")
            raise e
