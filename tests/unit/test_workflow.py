import traceback
from typing import Dict
from unittest.mock import MagicMock, patch

import pytest
from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import (
    SandboxedWorkflowRunner,
    SandboxRestrictions,
)

from app.workflow import ExtractionWorkflow
from sdk.dto.workflow import ExtractionConfig, WorkflowConfig


@pytest.mark.asyncio
async def test_extraction_workflow():
    workflow_config = WorkflowConfig(
        workflowId="test_workflow",
        credentialsGUID="credential_1234",
        includeFilterStr="{}",
        excludeFilterStr="{}",
        tempTableRegexStr="[]",
        outputPrefix="/tmp/test_output",
    )

    with patch("app.preflight.Preflight.prepare_filters") as mock_prepare_filters:
        mock_prepare_filters.return_value = (
            "include_regex",
            "exclude_regex",
            "exclude_table",
        )

        mock_setup_output_directory = MagicMock()
        mock_setup_output_directory.return_value = None
        mock_extract_metadata = MagicMock()
        mock_extract_metadata.return_value = {
            "test_typename": {"raw": 1, "transformed": 1, "errored": 0}
        }
        mock_push_results_to_object_store = MagicMock()
        mock_push_results_to_object_store.return_value = None

        mock_teardown_output_directory = MagicMock()
        mock_teardown_output_directory.return_value = None

        @activity.defn(name="setup_output_directory")
        async def wrapped_mock_setup_output_directory(output_path: str):
            mock_setup_output_directory(output_path)

        @activity.defn(name="extract_metadata")
        async def wrapped_mock_extract_metadata(config: ExtractionConfig):
            return mock_extract_metadata(config)

        @activity.defn(name="push_results_to_object_store")
        async def wrapped_mock_push_results_to_object_store(
            output_config: Dict[str, str],
        ):
            mock_push_results_to_object_store(output_config)

        @activity.defn(name="teardown_output_directory")
        async def wrapped_mock_teardown_output_directory(output_path: str):
            mock_teardown_output_directory(output_path)

        try:
            env = await WorkflowEnvironment.start_local()
            async with Worker(
                env.client,
                task_queue="test_queue",
                workflows=[ExtractionWorkflow],
                activities=[
                    wrapped_mock_setup_output_directory,
                    wrapped_mock_extract_metadata,
                    wrapped_mock_push_results_to_object_store,
                    wrapped_mock_teardown_output_directory,
                ],
                workflow_runner=SandboxedWorkflowRunner(
                    restrictions=SandboxRestrictions.default.with_passthrough_modules(
                        "sdk"
                    )
                ),
            ):
                result = await env.client.execute_workflow(  # pyright: ignore[reportUnknownMemberType]
                    ExtractionWorkflow.run,
                    workflow_config,
                    id="test_workflow",
                    task_queue="test_queue",
                )

        except Exception as e:
            print(f"Error during workflow execution: {e}")
            print(f"Error type: {type(e)}")
            print(f"Error traceback: {traceback.format_exc()}")
            raise e

    assert result is None

    assert mock_setup_output_directory.call_count == 1
    assert mock_extract_metadata.call_count == 5  # Once for each metadata type
    assert mock_push_results_to_object_store.call_count == 1
    assert mock_teardown_output_directory.call_count == 1
