import json
import os
from typing import Any, Dict, List

import pytest

from app.transformers.atlas import SQLAtlasTransformer

column_attributes = [
    "qualifiedName",
    "name",
    "tenantId",
    "connectorName",
    "connectionName",
    "connectionQualifiedName",
    "lastSyncWorkflowName",
    "lastSyncRun",
    "databaseName",
    "databaseQualifiedName",
    "schemaName",
    "schemaQualifiedName",
    "tableName",
    "tableQualifiedName",
    "viewName",
    "viewQualifiedName",
    "dataType",
    "order",
    "isPartition",
    "isPrimary",
    "isForeign",
    "isNullable",
    "numericScale",
    "maxLength",
    "isIdentity",
    "identityCycle",
]


@pytest.fixture
def resources_dir():
    return os.path.join(os.path.dirname(__file__), "resources")


@pytest.fixture
def raw_data(resources_dir: str) -> Dict[str, Any]:
    with open(os.path.join(resources_dir, "raw_postgres_columns.json")) as f:
        return json.load(f)


@pytest.fixture
def expected_data(resources_dir: str) -> Dict[str, Any]:
    with open(os.path.join(resources_dir, "transformed_postgres_columns.json")) as f:
        return json.load(f)


@pytest.fixture
def transformer():
    return SQLAtlasTransformer(connector_name="postgres", tenant_id="default")


def assert_attributes(
    transformed_data: Dict[str, Any],
    expected_data: Dict[str, Any],
    attributes: List[str],
    is_custom: bool = False,
):
    attr_type = "customAttributes" if is_custom else "attributes"
    for attr in attributes:
        if (
            attr not in transformed_data[attr_type]
            and attr not in expected_data[attr_type]
        ):
            continue
        assert (
            transformed_data[attr_type][attr] == expected_data[attr_type][attr]
        ), f"Mismatch in {'custom ' if is_custom else ''}{attr}"


def test_column_variation_1(
    transformer: SQLAtlasTransformer,
    raw_data: Dict[str, Any],
    expected_data: Dict[str, Any],
):
    """Test column transformation with custom attributes"""

    transformed_data = transformer.transform_row(
        "COLUMN",
        raw_data["postgres_column_1"],
        "test_workflow_id",
        "test_run_id",
        connection_name="test-connection",
        connection_qualified_name="default/postgres/1741637459",
    )

    assert transformed_data is not None
    expected_column = expected_data["postgres_column_1"]

    custom_attributes = [
        "ordinal_position",
        "is_self_referencing",
        "type_name",
        "is_auto_increment",
        "is_generated",
        "column_size",
    ]
    assert_attributes(
        transformed_data, expected_column, custom_attributes, is_custom=True
    )
    assert_attributes(transformed_data, expected_column, column_attributes)
    assert "lastSyncRunAt" in transformed_data["attributes"]
    assert transformed_data["attributes"]["lastSyncRunAt"] is not None

    # Test materialized view relationship
    assert "table" in transformed_data["attributes"]
    assert (
        transformed_data["attributes"]["table"]["uniqueAttributes"]["qualifiedName"]
        == expected_column["attributes"]["table"]["uniqueAttributes"]["qualifiedName"]
    )


def test_column_variation_2(
    transformer: SQLAtlasTransformer,
    raw_data: Dict[str, Any],
    expected_data: Dict[str, Any],
):
    """Test column transformation with custom attributes"""

    transformed_data = transformer.transform_row(
        "COLUMN",
        raw_data["postgres_column_2"],
        "test_workflow_id",
        "test_run_id",
        connection_name="test-connection",
        connection_qualified_name="default/postgres/1741637459",
    )

    assert transformed_data is not None
    expected_column = expected_data["postgres_column_2"]

    custom_attributes = [
        "ordinal_position",
        "is_self_referencing",
        "type_name",
        "is_auto_increment",
        "is_generated",
        "column_size",
    ]
    assert_attributes(
        transformed_data, expected_column, custom_attributes, is_custom=True
    )
    assert_attributes(transformed_data, expected_column, column_attributes)
    assert "lastSyncRunAt" in transformed_data["attributes"]
    assert transformed_data["attributes"]["lastSyncRunAt"] is not None

    # Test materialized view relationship
    assert "table" in transformed_data["attributes"]
    assert (
        transformed_data["attributes"]["table"]["uniqueAttributes"]["qualifiedName"]
        == expected_column["attributes"]["table"]["uniqueAttributes"]["qualifiedName"]
    )
