import json
import os
from typing import Any, Dict, List

import pytest

from app.transformers.atlas import SQLAtlasTransformer

table_attributes = [
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
    "columnCount",
    "rowCount",
    "sizeBytes",
    "externalLocation",
    "externalLocationRegion",
    "externalLocationFormat",
    "isPartitioned",
    "partitionStrategy",
    "partitionCount",
]
table_custom_attributes = [
    "table_type",
    "is_insertable_into",
    "number_columns_in_part_key",
    "columns_participating_in_part_key",
    "is_typed",
    "engine",
]


@pytest.fixture
def resources_dir():
    return os.path.join(os.path.dirname(__file__), "resources")


@pytest.fixture
def raw_data(resources_dir: str) -> Dict[str, Any]:
    with open(os.path.join(resources_dir, "raw_postgres_tables.json")) as f:
        return json.load(f)


@pytest.fixture
def expected_data(resources_dir: str) -> Dict[str, Any]:
    with open(os.path.join(resources_dir, "transformed_postgres_tables.json")) as f:
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


def test_table_variation_1_transformation(
    transformer: SQLAtlasTransformer,
    raw_data: Dict[str, Any],
    expected_data: Dict[str, Any],
):
    """Test the transformation of regular tables"""

    transformed_data = transformer.transform_row(
        "TABLE",
        raw_data["table_variation_1"],
        "test_workflow_id",
        "test_run_id",
        connection_name="test-connection",
        connection_qualified_name="default/postgres/1728518400",
    )

    assert transformed_data is not None
    expected_table = expected_data["table_variation_1"]

    # Basic type assertion
    assert transformed_data["typeName"] == "Table"

    assert_attributes(transformed_data, expected_table, table_attributes)

    assert_attributes(
        transformed_data, expected_table, table_custom_attributes, is_custom=True
    )
