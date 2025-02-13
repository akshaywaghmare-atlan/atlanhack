import asyncio
from datetime import timedelta
from typing import Any, Callable, Dict, List

from application_sdk.common.logger_adaptors import get_logger
from application_sdk.inputs.statestore import StateStoreInput
from application_sdk.workflows.metadata_extraction.sql import (
    SQLMetadataExtractionWorkflow,
)
from temporalio import workflow
from temporalio.common import RetryPolicy

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
        workflow_id = workflow_config["workflow_id"]
        workflow_args: Dict[str, Any] = StateStoreInput.extract_configuration(
            workflow_id
        )

        workflow_run_id = workflow.info().run_id
        workflow_args["workflow_run_id"] = workflow_run_id

        workflow.logger.info(f"Starting extraction workflow for {workflow_id}")
        retry_policy = RetryPolicy(
            maximum_attempts=6,
            backoff_coefficient=2,
        )

        output_prefix = workflow_args["output_prefix"]
        output_path = f"{output_prefix}/{workflow_id}/{workflow_run_id}"
        workflow_args["output_path"] = output_path

        await workflow.execute_activity_method(
            self.activities_cls.preflight_check,
            workflow_args,
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(seconds=1000),
        )

        fetch_and_transforms = [
            self.fetch_and_transform(
                self.activities_cls.fetch_databases,
                workflow_args,
                retry_policy,
                start_to_close_timeout_seconds=7200,  # 2 hours
            ),
            self.fetch_and_transform(
                self.activities_cls.fetch_schemas,
                workflow_args,
                retry_policy,
                start_to_close_timeout_seconds=7200,
            ),
            self.fetch_and_transform(
                self.activities_cls.fetch_tables,
                workflow_args,
                retry_policy,
                start_to_close_timeout_seconds=7200,
            ),
            self.fetch_and_transform(
                self.activities_cls.fetch_columns,
                workflow_args,
                retry_policy,
                start_to_close_timeout_seconds=7200,
            ),
            self.fetch_and_transform(
                self.activities_cls.fetch_procedures,
                workflow_args,
                retry_policy,
                start_to_close_timeout_seconds=7200,
            ),
        ]
        await asyncio.gather(*fetch_and_transforms)

    @staticmethod
    def get_activities(
        activities: PostgresMetadataExtractionActivities,
    ) -> List[Callable[..., Any]]:
        return [
            activities.preflight_check,
            activities.fetch_databases,
            activities.fetch_schemas,
            activities.fetch_tables,
            activities.fetch_columns,
            activities.fetch_procedures,
            activities.transform_data,
        ]
