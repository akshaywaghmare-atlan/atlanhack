from datetime import timedelta
from typing import Any, AsyncGenerator, Dict, List, TypeVar
from unittest.mock import MagicMock

import pytest
from pyatlan.model import assets
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from app.workflow import (
    CustomTransformer,
    PostgresActivities,
    PostgreSQLClient,
    PostgresTable,
    PostgresWorkflowHandler,
)

# Type variables for activity results
T = TypeVar("T")
ActivityResult = List[Dict[str, str]]


def test_postgres_client_connection_string():
    """Test PostgreSQLClient connection string generation"""
    credentials = {
        "user": "test_user",
        "password": "test@pass!123",
        "host": "localhost",
        "port": "5432",
        "database": "test_db",
    }

    client = PostgreSQLClient()
    client.credentials = credentials

    expected = "postgresql+psycopg://test_user:test%40pass%21123@localhost:5432/test_db"
    assert client.get_sqlalchemy_connection_string() == expected


def test_postgres_workflow_handler_sql_queries():
    """Test PostgresWorkflowHandler SQL query attributes"""
    from app.const import FILTER_METADATA_SQL, TABLES_CHECK_SQL

    handler = PostgresWorkflowHandler(sql_client=MagicMock())

    assert handler.metadata_sql == FILTER_METADATA_SQL
    assert handler.tables_check_sql == TABLES_CHECK_SQL


def test_postgres_activities_sql_queries():
    """Test PostgresActivities SQL query attributes"""
    from app.const import (
        COLUMN_EXTRACTION_SQL,
        DATABASE_EXTRACTION_SQL,
        SCHEMA_EXTRACTION_SQL,
        TABLE_EXTRACTION_SQL,
    )

    activities = PostgresActivities(
        sql_client_class=PostgreSQLClient,
        handler_class=PostgresWorkflowHandler,
        transformer_class=CustomTransformer,
    )

    assert activities.fetch_database_sql == DATABASE_EXTRACTION_SQL
    assert activities.fetch_schema_sql == SCHEMA_EXTRACTION_SQL
    assert activities.fetch_table_sql == TABLE_EXTRACTION_SQL
    assert activities.fetch_column_sql == COLUMN_EXTRACTION_SQL


class TestPostgresTable:
    def test_parse_regular_table(self):
        """Test parsing a regular table object"""
        table_data = {
            "table_type": "BASE TABLE",
            "table_name": "test_table",
            "table_schema": "public",
            "table_catalog": "test_db",
            "connection_qualified_name": "default/postgres/test-connection",
        }

        result = PostgresTable.parse_obj(table_data)
        assert isinstance(result, assets.Table)

    def test_parse_view(self):
        """Test parsing a view object"""
        view_data = {
            "table_type": "VIEW",
            "table_name": "test_view",
            "view_definition": "SELECT * FROM base_table",
            "table_schema": "public",
            "table_catalog": "test_db",
            "connection_qualified_name": "default/postgres/test-connection",
        }

        result = PostgresTable.parse_obj(view_data)
        assert isinstance(result, assets.View)
        assert (
            result.attributes.definition
            == "CREATE OR REPLACE VIEW test_view AS SELECT * FROM base_table"
        )

    def test_parse_materialized_view(self):
        """Test parsing a materialized view object"""
        mview_data = {
            "table_type": "MATERIALIZED VIEW",
            "table_name": "test_mview",
            "view_definition": "SELECT * FROM base_table",
            "table_schema": "public",
            "table_catalog": "test_db",
            "connection_qualified_name": "default/postgres/test-connection",
        }

        result = PostgresTable.parse_obj(mview_data)
        assert isinstance(result, assets.MaterialisedView)
        assert (
            result.attributes.definition
            == "CREATE OR REPLACE MATERIALIZED VIEW test_mview AS SELECT * FROM base_table"
        )


def test_custom_transformer_initialization():
    """Test CustomTransformer initialization and entity class mappings"""
    transformer = CustomTransformer(
        connector_name="test-connector", tenant_id="test-tenant"
    )

    assert transformer.entity_class_definitions["TABLE"] == PostgresTable
    assert transformer.entity_class_definitions["VIEW"] == PostgresTable
    assert transformer.entity_class_definitions["MATERIALIZED VIEW"] == PostgresTable


# Mock activities for testing
@activity.defn
async def fetch_databases() -> ActivityResult:
    return [{"name": "test_db"}]


@activity.defn
async def fetch_schemas() -> ActivityResult:
    return [{"name": "public"}]


@activity.defn
async def fetch_tables() -> ActivityResult:
    return [
        {
            "table_type": "BASE TABLE",
            "table_name": "test_table",
            "table_schema": "public",
            "table_catalog": "test_db",
            "connection_qualified_name": "default/postgres/test-connection",
        }
    ]


@activity.defn
async def fetch_columns() -> ActivityResult:
    return [{"column_name": "id", "data_type": "integer"}]


@workflow.defn(sandboxed=False)
class MockExtractionWorkflow:
    @workflow.run
    async def run(self, config: Dict[str, Any]) -> Dict[str, Any]:
        # Execute activities and collect results
        databases = await workflow.execute_activity(  # type: ignore
            fetch_databases, start_to_close_timeout=timedelta(seconds=30)
        )

        schemas = await workflow.execute_activity(  # type: ignore
            fetch_schemas, start_to_close_timeout=timedelta(seconds=30)
        )

        tables = await workflow.execute_activity(  # type: ignore
            fetch_tables, start_to_close_timeout=timedelta(seconds=30)
        )

        columns = await workflow.execute_activity(  # type: ignore
            fetch_columns, start_to_close_timeout=timedelta(seconds=30)
        )

        return {
            "status": "completed",
            "config": config,
            "data": {
                "databases": databases,
                "schemas": schemas,
                "tables": tables,
                "columns": columns,
            },
        }


class TestPostgresWorkflow:
    @pytest.fixture
    async def workflow_env(self) -> AsyncGenerator[Client, None]:
        """Create a test workflow environment."""
        env = await WorkflowEnvironment.start_local()
        try:
            yield env.client
        finally:
            await env.shutdown()

    @pytest.mark.asyncio
    async def test_extraction_workflow(self, workflow_env: Client) -> None:
        """Test the complete extraction workflow execution"""
        # Setup workflow config
        workflow_config = {
            "connection_qualified_name": "default/postgres/test-connection",
            "output_path": "/tmp/test_output",
            "tenant_id": "test-tenant",
        }

        # Create worker with workflow and activities
        worker = Worker(
            workflow_env,
            task_queue="test-queue",
            workflows=[MockExtractionWorkflow],
            activities=[fetch_databases, fetch_schemas, fetch_tables, fetch_columns],
        )

        async with worker:
            # Run the workflow
            result = await workflow_env.execute_workflow(  # type: ignore
                MockExtractionWorkflow.run,
                workflow_config,
                id="test-workflow",
                task_queue="test-queue",
            )

            # Verify workflow completion
            assert result is not None
            assert result["status"] == "completed"
            assert result["config"] == workflow_config

            # Verify activity results are present
            assert "data" in result
            assert "databases" in result["data"]
            assert "schemas" in result["data"]
            assert "tables" in result["data"]
            assert "columns" in result["data"]
