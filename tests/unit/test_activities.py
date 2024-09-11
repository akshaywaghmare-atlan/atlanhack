import pytest
import os
from unittest.mock import patch, MagicMock
from app.workflow.activities import ExtractionActivities
from app.dto.workflow import ExtractionConfig, WorkflowConfig

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_dapr_client():
    """
    Fixture to mock the DaprClient for testing.

    Returns:
        MagicMock: A mocked instance of DaprClient.
    """
    with patch("sdk.interfaces.platform.DaprClient") as mock:
        yield mock.return_value


@pytest.fixture
def mock_platform():
    """
    Fixture to mock the Platform class.

    Returns:
        MagicMock: A mock object for the Platform class.
    """
    with patch("app.workflow.activities.Platform") as mock:
        yield mock


@pytest.fixture
def mock_connect_to_db():
    """
    Fixture to mock the connect_to_db function.

    Returns:
        MagicMock: A mock object for the connect_to_db function.
    """
    with patch("app.workflow.activities.connect_to_db") as mock:
        yield mock


@pytest.mark.asyncio
async def test_create_output_directory():
    """
    Test the create_output_directory method of ExtractionActivities.

    Ensures that the method creates the expected directory structure.
    """
    output_prefix = "/tmp/test_output"

    with patch("os.makedirs") as mock_makedirs:
        await ExtractionActivities.create_output_directory(output_prefix)

        assert mock_makedirs.call_count == 3
        mock_makedirs.assert_any_call(output_prefix, exist_ok=True)
        mock_makedirs.assert_any_call(os.path.join(output_prefix, "raw"), exist_ok=True)
        mock_makedirs.assert_any_call(
            os.path.join(output_prefix, "transformed"), exist_ok=True
        )


@pytest.mark.asyncio
async def test_extract_and_store_metadata(mock_platform, mock_connect_to_db):
    """
    Test the extract_and_store_metadata method of ExtractionActivities.

    Verifies that the method correctly extracts metadata, stores it in files,
    and returns the expected result.

    Args:
        mock_platform (MagicMock): Mocked Platform object.
        mock_connect_to_db (MagicMock): Mocked connect_to_db function.
    """
    workflow_config = WorkflowConfig(
        workflowId="test_workflow",
        outputPath="/tmp/test_output/test_workflow/test_run",
        outputPrefix="/tmp/test_output",
        credentialsGUID="test_guid",
        includeFilterStr="",
        excludeFilterStr="",
        tempTableRegexStr="",
    )

    ext_config = ExtractionConfig(
        workflowConfig=workflow_config, typename="table", query="SELECT * FROM tables"
    )

    mock_cursor = MagicMock()
    # Set up the mock to return data only once, then empty list
    mock_cursor.fetchmany.side_effect = [
        [
            ("table1", "table_cat1", "table_schem1"),
            ("table2", "table_cat2", "table_schem2"),
        ],
        [],
    ]
    mock_cursor.description = [["table_name"], ["table_cat"], ["table_schem"]]

    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect_to_db.return_value = mock_conn

    with patch("builtins.open", create=True) as mock_open:
        result = await ExtractionActivities.extract_and_store_metadata(ext_config)

        assert result == {"table": {"raw": 2, "transformed": 2, "errored": 0}}

        mock_platform.extract_credentials.assert_called_once_with("test_guid")
        mock_connect_to_db.assert_called_once()
        mock_cursor.execute.assert_called_once_with("SELECT * FROM tables")

        assert mock_open.call_count == 2
        mock_open.assert_any_call(
            os.path.join(
                "/tmp/test_output/test_workflow/test_run", "raw", "table.json"
            ),
            "w",
        )
        mock_open.assert_any_call(
            os.path.join(
                "/tmp/test_output/test_workflow/test_run", "transformed", "table.json"
            ),
            "w",
        )


@pytest.mark.asyncio
async def test_push_results_to_object_store(mock_platform):
    """
    Test the push_results_to_object_store method of ExtractionActivities.

    Ensures that the method calls the platform's push_to_object_store
    with the correct arguments.

    Args:
        mock_platform (MagicMock): Mocked Platform object.
    """
    output_config = {
        "output_prefix": "/tmp/test_output",
        "output_path": "/tmp/test_output/test_workflow",
    }

    await ExtractionActivities.push_results_to_object_store(output_config)

    mock_platform.push_to_object_store.assert_called_once_with(
        "/tmp/test_output", "/tmp/test_output/test_workflow"
    )
