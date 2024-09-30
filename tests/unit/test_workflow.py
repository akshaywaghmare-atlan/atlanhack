import traceback
from typing import Any, Dict
from unittest.mock import MagicMock

import pytest
from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker
from temporalio.worker.workflow_sandbox import (
    SandboxedWorkflowRunner,
    SandboxRestrictions,
)

from app.workflow import PostgresWorkflowWorker


@pytest.mark.asyncio
async def test_extraction_workflow():
    workflow_config = {
        "workflow_id": "test_workflow",
        "credentials_guid": "credential_1234",
        "output_prefix": "/tmp/test_output",
        "connection": {"connection": "dev"},
        "metadata": {
            "exclude-filter": "{}",
            "include-filter": "{}",
            "temp-table-regex": "",
            "advanced-config-strategy": "default",
            "use-source-schema-filtering": "false",
            "use-jdbc-internal-methods": "true",
            "authentication": "BASIC",
            "extraction-method": "direct",
        },
    }

    mock_setup_output_directory = MagicMock()
    mock_setup_output_directory.return_value = None

    mock_fetch_databases = MagicMock()
    mock_fetch_databases.return_value = {
        "database": {"raw": 1, "transformed": 1, "errored": 0}
    }

    mock_fetch_schemas = MagicMock()
    mock_fetch_schemas.return_value = {
        "schema": {"raw": 1, "transformed": 1, "errored": 0}
    }

    mock_fetch_tables = MagicMock()
    mock_fetch_tables.return_value = {
        "table": {"raw": 1, "transformed": 1, "errored": 0}
    }

    mock_fetch_columns = MagicMock()
    mock_fetch_columns.return_value = {
        "column": {"raw": 1, "transformed": 1, "errored": 0}
    }

    mock_push_results_to_object_store = MagicMock()
    mock_push_results_to_object_store.return_value = None

    mock_teardown_output_directory = MagicMock()
    mock_teardown_output_directory.return_value = None

    @activity.defn(name="setup_output_directory")
    async def wrapped_mock_setup_output_directory(output_path: str):
        mock_setup_output_directory(output_path)

    @activity.defn(name="fetch_databases")
    async def wrapped_mock_fetch_databases(workflow_config: Dict[str, Any]):
        return mock_fetch_databases(workflow_config)

    @activity.defn(name="fetch_schemas")
    async def wrapped_mock_fetch_schemas(workflow_config: Dict[str, Any]):
        return mock_fetch_schemas(workflow_config)

    @activity.defn(name="fetch_tables")
    async def wrapped_mock_fetch_tables(workflow_config: Dict[str, Any]):
        return mock_fetch_tables(workflow_config)

    @activity.defn(name="fetch_columns")
    async def wrapped_mock_fetch_columns(workflow_config: Dict[str, Any]):
        return mock_fetch_columns(workflow_config)

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
            workflows=[PostgresWorkflowWorker],
            activities=[
                wrapped_mock_setup_output_directory,
                wrapped_mock_fetch_databases,
                wrapped_mock_fetch_schemas,
                wrapped_mock_fetch_tables,
                wrapped_mock_fetch_columns,
                wrapped_mock_push_results_to_object_store,
                wrapped_mock_teardown_output_directory,
            ],
            workflow_runner=SandboxedWorkflowRunner(
                restrictions=SandboxRestrictions.default.with_passthrough_modules(
                    "application_sdk"
                )
            ),
        ):
            result = await env.client.execute_workflow(  # pyright: ignore[reportUnknownMemberType]
                PostgresWorkflowWorker.run,
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
    assert mock_fetch_databases.call_count == 1
    assert mock_fetch_schemas.call_count == 1
    assert mock_fetch_tables.call_count == 1
    assert mock_fetch_columns.call_count == 1
    assert mock_push_results_to_object_store.call_count == 1
    assert mock_teardown_output_directory.call_count == 1
