from typing import Any, Dict

from application_sdk.transformers.atlas import AtlasTransformer
from application_sdk.transformers.atlas.sql import Column, Procedure, Table


class PostgresTable(Table):
    @classmethod
    def get_attributes(cls, obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Postgres view and materialized view definitions are select queries,
        so we need to format the view definition to be a valid SQL query.

        src: https://github.com/atlanhq/marketplace-packages/blob/master/packages/atlan/postgres/transformers/view.jinja2
        """
        assert "table_name" in obj, "table_name cannot be None"
        assert "table_type" in obj, "table_type cannot be None"

        entity_data = super().get_attributes(obj)
        table_attributes = entity_data.get("attributes", {})
        table_custom_attributes = entity_data.get("custom_attributes", {})

        table_attributes["constraint"] = obj.get("partition_constraint", "")

        if (
            obj.get("table_kind", "") == "p"
            or obj.get("table_type", "") == "PARTITIONED TABLE"
        ):
            table_attributes["is_partitioned"] = True
            table_attributes["partition_strategy"] = obj.get("partition_strategy", "")
            table_attributes["partition_count"] = obj.get("partition_count", 0)
        else:
            table_attributes["is_partitioned"] = False

        table_custom_attributes["is_insertable_into"] = obj.get(
            "is_insertable_into", False
        )
        table_custom_attributes["is_typed"] = obj.get("is_typed", False)
        table_custom_attributes["self_referencing_col_name"] = obj.get(
            "self_referencing_col_name", ""
        )
        table_custom_attributes["ref_generation"] = obj.get("ref_generation", "")
        if obj.get("table_type") == "VIEW":
            view_definition = "CREATE OR REPLACE VIEW {view_name} AS {query}"
            table_attributes["definition"] = view_definition.format(
                view_name=obj.get("table_name", ""),
                query=obj.get("view_definition", ""),
            )
        elif obj.get("table_type") == "MATERIALIZED VIEW":
            view_definition = "CREATE MATERIALIZED VIEW {view_name} AS {query}"
            table_attributes["definition"] = view_definition.format(
                view_name=obj.get("table_name", ""),
                query=obj.get("view_definition", ""),
            )

        entity_class = None
        if entity_data["entity_class"] == Table:
            entity_class = PostgresTable
        else:
            entity_class = entity_data["entity_class"]

        return {
            **entity_data,
            "attributes": table_attributes,
            "custom_attributes": table_custom_attributes,
            "entity_class": entity_class,
        }


class PostgresColumn(Column):
    @classmethod
    def get_attributes(cls, obj: Dict[str, Any]) -> Dict[str, Any]:
        entity_data = super().get_attributes(obj)

        column_attributes = entity_data.get("attributes", {})
        column_custom_attributes = entity_data.get("custom_attributes", {})

        if obj.get("numeric_precision_radix", "") != "":
            column_custom_attributes["num_prec_radix"] = obj.get(
                "numeric_precision_radix", ""
            )
        if obj.get("is_identity", "") != "":
            column_custom_attributes["is_identity"] = obj.get("is_identity", "")
        if obj.get("identity_cycle", "") != "":
            column_custom_attributes["identity_cycle"] = obj.get("identity_cycle", "")

        if obj.get("constraint_type", "") == "PRIMARY KEY":
            column_attributes["is_primary"] = True

        elif obj.get("constraint_type", "") == "FOREIGN KEY":
            column_attributes["is_foreign"] = True

        return {
            **entity_data,
            "attributes": column_attributes,
            "custom_attributes": column_custom_attributes,
            "entity_class": PostgresColumn,
        }


class PostgresAtlasTransformer(AtlasTransformer):
    def __init__(self, connector_name: str, tenant_id: str, **kwargs: Any):
        super().__init__(connector_name, tenant_id, **kwargs)

        self.entity_class_definitions["TABLE"] = PostgresTable
        self.entity_class_definitions["COLUMN"] = PostgresColumn
        self.entity_class_definitions["EXTRAS-PROCEDURE"] = Procedure
