import asyncio
from datetime import timedelta
from typing import Any, Coroutine, Dict, List

from temporalio import workflow
from temporalio.common import RetryPolicy

from app.activities import ExtractionActivities
from app.const import (
    COLUMN_EXTRACTION_SQL,
    DATABASE_EXTRACTION_SQL,
    PROCEDURE_EXTRACTION_SQL,
    SCHEMA_EXTRACTION_SQL,
    TABLE_EXTRACTION_SQL,
)
from app.preflight import Preflight
from sdk.dto.workflow import ExtractionConfig, WorkflowConfig


@workflow.defn
class ExtractionWorkflow:
    @workflow.run
    async def run(self, config: WorkflowConfig) -> None:
        workflow.logger.info(f"Starting extraction workflow for {config.workflowId}")
        retry_policy = RetryPolicy(
            maximum_attempts=6,
            backoff_coefficient=2,
        )

        workflow_run_id = workflow.info().run_id
        config.outputPath = (
            f"{config.outputPrefix}/{config.workflowId}/{workflow_run_id}"
        )

        # Create output directory
        await workflow.execute_activity(  # pyright: ignore[reportUnknownMemberType]
            ExtractionActivities.create_output_directory,
            config.outputPath,
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(seconds=5),
        )

        # Define metadata types and their corresponding queries
        normalized_include_regex, normalized_exclude_regex, exclude_table = (
            Preflight.prepare_filters(
                config.includeFilterStr,
                config.excludeFilterStr,
                config.tempTableRegexStr,
            )
        )
        metadata_types = {
            "database": DATABASE_EXTRACTION_SQL,
            "schema": SCHEMA_EXTRACTION_SQL.format(
                normalized_include_regex=normalized_include_regex,
                normalized_exclude_regex=normalized_exclude_regex,
            ),
            "table": TABLE_EXTRACTION_SQL.format(
                normalized_include_regex=normalized_include_regex,
                normalized_exclude_regex=normalized_exclude_regex,
                exclude_table=exclude_table,
            ),
            "column": COLUMN_EXTRACTION_SQL.format(
                normalized_include_regex=normalized_include_regex,
                normalized_exclude_regex=normalized_exclude_regex,
                exclude_table=exclude_table,
            ),
            "procedure": PROCEDURE_EXTRACTION_SQL.format(
                normalized_include_regex=normalized_include_regex,
                normalized_exclude_regex=normalized_exclude_regex,
            ),
        }

        # Extract and store metadata for each type
        activities: List[Coroutine[Any, Any, Any]] = []
        for typename, query in metadata_types.items():
            activities.append(
                workflow.execute_activity(  # pyright: ignore[reportUnknownMemberType]
                    ExtractionActivities.extract_metadata,
                    ExtractionConfig(
                        workflowConfig=config, typename=typename, query=query
                    ),
                    retry_policy=retry_policy,
                    # https://community.temporal.io/t/long-running--with-auto-heartbeater-failing/13586
                    heartbeat_timeout=timedelta(minutes=1),
                    start_to_close_timeout=timedelta(minutes=600),
                )
            )

        # Wait for all activities to complete
        results = await asyncio.gather(*activities)
        extraction_results: Dict[str, Any] = {}
        for result in results:
            extraction_results.update(result)

        # Push results to object store
        await workflow.execute_activity(  # pyright: ignore[reportUnknownMemberType]
            ExtractionActivities.push_results_to_object_store,
            {"output_prefix": config.outputPrefix, "output_path": config.outputPath},
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(minutes=10),
        )

        # TODO: cleanup output directory
        workflow.logger.info(f"Extraction workflow completed for {config.workflowId}")
        workflow.logger.info(f"Extraction results summary: {extraction_results}")
