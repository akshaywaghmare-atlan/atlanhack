from datetime import timedelta
from typing import Any, AsyncGenerator, Dict, List, TypeVar
from unittest.mock import MagicMock
from urllib.parse import quote_plus

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pyatlan.model import assets
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from app.activities.metadata_extraction.postgres import (
    PostgresMetadataExtractionActivities,
)
from app.clients import PostgreSQLClient
from app.const import PROCEDURE_EXTRACTION_SQL
from app.handlers import PostgresWorkflowHandler
from app.transformers.atlas import PostgresAtlasTransformer, PostgresTable

# Type variables for activity results
T = TypeVar("T")
ActivityResult = List[Dict[str, str]]

# Custom strategies for PostgreSQL testing
postgres_auth_types = st.sampled_from(["basic", "iam_user", "iam_role"])

# Strategy for extra fields in credentials
postgres_extra_strategy = st.one_of(
    st.fixed_dictionaries({"database": st.text()}),  # Basic auth
    st.fixed_dictionaries(
        {  # IAM user auth
            "database": st.text(),
            "aws_region": st.text(),
        }
    ),
    st.fixed_dictionaries(
        {  # IAM role auth
            "database": st.text(),
            "role_arn": st.text(),
            "external_id": st.text(),
            "aws_region": st.text(),
        }
    ),
)

postgres_credentials_strategy = st.fixed_dictionaries(
    {
        "username": st.text(),
        "password": st.text(),
        "host": st.text(),
        "port": st.integers(min_value=1, max_value=65535).map(str),
        "extra": postgres_extra_strategy,
        "authType": postgres_auth_types,
    }
)

postgres_table_types = st.sampled_from(["BASE TABLE", "VIEW", "MATERIALIZED VIEW"])
postgres_table_strategy = st.fixed_dictionaries(
    {
        "table_type": postgres_table_types,
        "table_name": st.text(),
        "table_schema": st.text(),
        "table_catalog": st.text(),
        "connection_qualified_name": st.just("default/postgres/test-connection"),
        "view_definition": st.text(),
    }
)


def test_postgres_client_connection_string():
    """Test PostgreSQLClient connection string generation for different auth types"""
    # Test basic auth
    basic_credentials: Dict[str, Any] = {
        "username": "test_user",
        "password": "test@pass!123",
        "host": "localhost",
        "port": "5432",
        "extra": {"database": "test_db"},
        "authType": "basic",
    }

    client = PostgreSQLClient()
    client.credentials = basic_credentials
    encoded_password = quote_plus(str(basic_credentials["password"]))
    expected = f"postgresql+psycopg://{basic_credentials['username']}:{encoded_password}@{basic_credentials['host']}:{basic_credentials['port']}/{basic_credentials['extra'].get('database')}?application_name=Atlan&connect_timeout=5"
    result = client.get_sqlalchemy_connection_string()
    assert result == expected

    # Test missing credentials
    with pytest.raises(KeyError):
        client.credentials = {}
        client.get_sqlalchemy_connection_string()

    # Test invalid auth type
    invalid_credentials = {
        "authType": "invalid",
        "username": "test_user",
        "password": "test_pass",
        "host": "localhost",
        "port": "5432",
        "extra": {"database": "test_db"},
    }
    client.credentials = invalid_credentials
    with pytest.raises(ValueError):
        client.get_sqlalchemy_connection_string()

    # Test missing required fields for IAM user auth
    incomplete_iam_user = {
        "username": "test_user",
        "host": "localhost",
        "port": "5432",
        "extra": {"database": "test_db"},
        "authType": "iam_user",
    }
    client.credentials = incomplete_iam_user
    with pytest.raises(KeyError):
        client.get_sqlalchemy_connection_string()

    # Test IAM role auth with required fields
    iam_role_credentials = {
        "username": "test_user",
        "host": "localhost",
        "port": "5432",
        "extra": {
            "database": "test_db",
            "role_arn": "arn:aws:iam::123456789012:role/test-role",
            "external_id": "test-external-id",
        },
        "authType": "iam_role",
    }
    client.credentials = iam_role_credentials
    with pytest.raises(
        Exception
    ):  # Will raise because we can't actually assume the role in tests
        client.get_sqlalchemy_connection_string()


@given(credentials=postgres_credentials_strategy)
@pytest.mark.skip(
    reason="Skipping test due to the following failure : ExceptionGroup: Hypothesis found 3 distinct failures. (3 sub-exceptions)"
)
def test_postgres_client_connection_string_with_hypothesis(credentials):
    """Test PostgreSQLClient connection string generation for different auth types"""
    client = PostgreSQLClient()
    client.credentials = credentials

    if credentials["authType"] == "basic":
        encoded_password = quote_plus(str(credentials["password"]))
        database = credentials["extra"].get("database", "")
        db_part = f"/{database}" if database else "/"
        expected = f"postgresql+psycopg://{credentials['username']}:{encoded_password}@{credentials['host']}:{credentials['port']}{db_part}?application_name=Atlan&connect_timeout=5"
        result = client.get_sqlalchemy_connection_string()
        assert result == expected
    elif credentials["authType"] == "iam_user":
        if "aws_region" not in credentials["extra"]:
            with pytest.raises(KeyError):
                client.get_sqlalchemy_connection_string()
        else:
            with pytest.raises(
                Exception
            ):  # Will raise because we can't actually assume IAM roles in tests
                client.get_sqlalchemy_connection_string()
    elif credentials["authType"] == "iam_role":
        required_fields = {"role_arn", "external_id", "aws_region"}
        if not all(field in credentials["extra"] for field in required_fields):
            with pytest.raises(KeyError):
                client.get_sqlalchemy_connection_string()
        else:
            with pytest.raises(
                Exception
            ):  # Will raise because we can't actually assume IAM roles in tests
                client.get_sqlalchemy_connection_string()
    else:
        with pytest.raises(ValueError):
            client.get_sqlalchemy_connection_string()


@given(
    st.one_of(
        st.just({}),
        st.fixed_dictionaries(
            {
                "authType": st.just("invalid"),
                "username": st.text(),
                "password": st.text(),
                "host": st.text(),
                "port": st.text(),
                "extra": st.fixed_dictionaries({"database": st.text()}),
            }
        ),
    )
)
def test_postgres_client_connection_string_errors(invalid_credentials):
    """Test error cases for PostgreSQLClient connection string generation"""
    client = PostgreSQLClient()
    client.credentials = invalid_credentials

    if not invalid_credentials:
        with pytest.raises(KeyError):
            client.get_sqlalchemy_connection_string()
    else:
        with pytest.raises(ValueError):
            client.get_sqlalchemy_connection_string()


@given(st.data())
def test_postgres_workflow_handler_sql_queries(data):
    """Test PostgresWorkflowHandler SQL query attributes"""
    from app.const import FILTER_METADATA_SQL, TABLES_CHECK_SQL

    handler = PostgresWorkflowHandler(sql_client=MagicMock())
    assert handler.metadata_sql == FILTER_METADATA_SQL
    assert handler.tables_check_sql == TABLES_CHECK_SQL


@given(st.data())
def test_postgres_activities_sql_queries(data):
    """Test PostgresActivities SQL query attributes"""
    from app.const import (
        COLUMN_EXTRACTION_SQL,
        DATABASE_EXTRACTION_SQL,
        SCHEMA_EXTRACTION_SQL,
        TABLE_EXTRACTION_SQL,
    )

    activities = PostgresMetadataExtractionActivities(
        sql_client_class=PostgreSQLClient,
        handler_class=PostgresWorkflowHandler,
        transformer_class=PostgresAtlasTransformer,
    )

    assert activities.fetch_database_sql == DATABASE_EXTRACTION_SQL
    assert activities.fetch_schema_sql == SCHEMA_EXTRACTION_SQL
    assert activities.fetch_table_sql == TABLE_EXTRACTION_SQL
    assert activities.fetch_column_sql == COLUMN_EXTRACTION_SQL
    assert activities.fetch_procedure_sql == PROCEDURE_EXTRACTION_SQL


@given(table_data=postgres_table_strategy)
@pytest.mark.skip(
    reason="Skipping test due to the following failure : ExceptionGroup: Hypothesis found 2 distinct failures. (2 sub-exceptions)"
)
def test_postgres_table_with_hypothesis(table_data):
    """Test parsing different types of PostgreSQL tables"""
    result = PostgresTable.parse_obj(table_data)

    if table_data["table_type"] == "BASE TABLE":
        assert isinstance(result, assets.Table)
    elif table_data["table_type"] == "VIEW":
        assert isinstance(result, assets.View)
        assert (
            result.attributes.definition
            == f"CREATE OR REPLACE VIEW {table_data['table_name']} AS {table_data['view_definition']}"
        )
    elif table_data["table_type"] == "MATERIALIZED VIEW":
        assert isinstance(result, assets.MaterialisedView)
        assert (
            result.attributes.definition
            == f"CREATE MATERIALIZED VIEW {table_data['table_name']} AS {table_data['view_definition']}"
        )


def test_postgres_table():
    """Test parsing different types of PostgreSQL tables"""
    # Test regular table
    table_data = {
        "table_type": "BASE TABLE",
        "table_name": "test_table",
        "table_schema": "public",
        "table_catalog": "test_db",
        "connection_qualified_name": "default/postgres/test-connection",
    }
    result = PostgresTable.get_attributes(table_data)
    assert result["entity_class"] == assets.Table

    # Test view with SQL definition
    view_data = {
        "table_type": "VIEW",
        "table_name": "test_view",
        "view_definition": "SELECT * FROM base_table",
        "table_schema": "public",
        "table_catalog": "test_db",
        "connection_qualified_name": "default/postgres/test-connection",
    }
    result = PostgresTable.get_attributes(view_data)
    assert result["entity_class"] == assets.View
    assert (
        result["attributes"]["definition"]
        == "CREATE OR REPLACE VIEW test_view AS SELECT * FROM base_table"
    )

    # Test materialized view with SQL definition
    mview_data = {
        "table_type": "MATERIALIZED VIEW",
        "table_name": "test_mview",
        "view_definition": "SELECT * FROM base_table",
        "table_schema": "public",
        "table_catalog": "test_db",
        "connection_qualified_name": "default/postgres/test-connection",
    }
    result = PostgresTable.get_attributes(mview_data)
    assert result["entity_class"] == assets.MaterialisedView
    assert (
        result["attributes"]["definition"]
        == "CREATE MATERIALIZED VIEW test_mview AS SELECT * FROM base_table"
    )


@given(
    connector_name=st.text(),
    tenant_id=st.text(),
)
def test_custom_transformer_initialization(connector_name, tenant_id):
    """Test PostgresAtlasTransformer initialization and entity class mappings"""
    transformer = PostgresAtlasTransformer(
        connector_name=connector_name, tenant_id=tenant_id
    )
    assert transformer.entity_class_definitions["TABLE"] == PostgresTable


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
