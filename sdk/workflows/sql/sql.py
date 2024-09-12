import logging

from sqlalchemy import create_engine, text

from sdk.workflows import WorkflowBuilderInterface
from abc import ABC, abstractmethod
from typing import Dict, Any

logger = logging.getLogger(__name__)


class SQLWorkflowBuilderInterface(WorkflowBuilderInterface, ABC):
    TEST_AUTHENTICATION_SQL = "SELECT 1;"
    FETCH_METADATA_SQL = ""

    @abstractmethod
    def get_sqlalchemy_connection_string(self, credentials: Dict[str, Any]) -> str:
        pass

    @abstractmethod
    def get_sqlalchemy_connect_args(
        self, credentials: Dict[str, Any]
    ) -> Dict[str, Any]:
        pass

    @abstractmethod
    def test_auth(self, credentials: Dict[str, Any]) -> bool:
        try:
            engine = create_engine(
                self.get_sqlalchemy_connection_string(credentials),
                connect_args=self.get_sqlalchemy_connect_args(credentials),
                pool_pre_ping=True,
            )
            with engine.connect() as connection:
                cursor = connection.execute(text(self.TEST_AUTHENTICATION_SQL))
                row = cursor.fetchone()
                return True if row else False
        except Exception as e:
            logger.error("Error during authentication test", exc_info=True)
            raise e

    @abstractmethod
    def preflight_check(self):
        pass

    @abstractmethod
    def fetch_metadata(self):
        pass
