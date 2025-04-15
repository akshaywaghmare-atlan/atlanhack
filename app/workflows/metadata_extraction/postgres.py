from typing import Any, Callable, Coroutine, Dict, List

from application_sdk.common.logger_adaptors import get_logger
from application_sdk.workflows.metadata_extraction.sql import (
    SQLMetadataExtractionWorkflow,
)
from temporalio import workflow

from app.activities.metadata_extraction.postgres import (
    PostgresMetadataExtractionActivities,
)

logger = get_logger(__name__)


@workflow.defn
class PostgresMetadataExtractionWorkflow(SQLMetadataExtractionWorkflow):
    activities_cls = PostgresMetadataExtractionActivities

    @workflow.run
    async def run(self, workflow_config: Dict[str, Any]):
        """
        Run the workflow.

        :param workflow_args: The workflow arguments.
        """
        await super().run(workflow_config)

    def get_fetch_functions(
        self,
    ) -> List[Callable[[Dict[str, Any]], Coroutine[Any, Any, Dict[str, Any]]]]:
        """Get the fetch functions for the Postgres metadata extraction workflow.

        Returns:
            List[Callable[[Dict[str, Any]], Coroutine[Any, Any, Dict[str, Any]]]]: A list of fetch operations.
        """
        base_functions = super().get_fetch_functions()
        return base_functions + [
            self.activities_cls.fetch_procedures,
        ]

    @staticmethod
    def get_activities(
        activities: PostgresMetadataExtractionActivities,
    ) -> List[Callable[..., Any]]:
        base_activities = SQLMetadataExtractionWorkflow.get_activities(activities)
        return base_activities + [
            activities.fetch_procedures,
        ]
