from typing import Any, Dict, Union

from application_sdk.transformers.atlas import AtlasTransformer
from application_sdk.transformers.atlas.sql import Column, Procedure, Table
from pyatlan.model import assets


class PostgresTable(Table):
    @classmethod
    def parse_obj(
        cls, obj: Dict[str, Any]
    ) -> Union[
        assets.Table,
        assets.View,
        assets.MaterialisedView,
        assets.SnowflakeDynamicTable,
        assets.TablePartition,
    ]:
        """
        Postgres view and materialized view definitions are select queries,
        so we need to format the view definition to be a valid SQL query.

        src: https://github.com/atlanhq/marketplace-packages/blob/master/packages/atlan/postgres/transformers/view.jinja2
        """
        assert "table_name" in obj, "table_name cannot be None"
        assert "table_type" in obj, "table_type cannot be None"

        table = super().parse_obj(obj)

        if hasattr(table, "constraint"):
            table.constraint = obj.get("partition_constraint", "")

        if (
            obj.get("table_kind", "") == "p"
            or obj.get("table_type", "") == "PARTITIONED TABLE"
        ):
            table.is_partitioned = True
            table.partition_strategy = obj.get("partition_strategy", "")
            table.partition_count = obj.get("partition_count", 0)
        elif hasattr(table, "is_partitioned"):
            table.is_partitioned = False

        if obj.get("is_partition", False):
            if obj.get("partitioned_parent_table", False):
                table.parent_table_partition = obj.get("partitioned_parent_table", "")
                pass
            else:
                table.parent_table = None
                pass

        if not table.custom_attributes:
            table.custom_attributes = {}

        table.custom_attributes["is_insertable_into"] = obj.get(
            "is_insertable_into", False
        )
        table.custom_attributes["is_typed"] = obj.get("is_typed", False)
        table.custom_attributes["self_referencing_col_name"] = obj.get(
            "self_referencing_col_name", ""
        )
        table.custom_attributes["ref_generation"] = obj.get("ref_generation", "")

        if obj.get("table_type") == "VIEW":
            view_definition = "CREATE OR REPLACE VIEW {view_name} AS {query}"
            table.attributes.definition = view_definition.format(
                view_name=obj.get("table_name", ""),
                query=obj.get("view_definition", ""),
            )
        elif obj.get("table_type") == "MATERIALIZED VIEW":
            view_definition = "CREATE MATERIALIZED VIEW {view_name} AS {query}"
            table.attributes.definition = view_definition.format(
                view_name=obj.get("table_name", ""),
                query=obj.get("view_definition", ""),
            )

        return table


class PostgresColumn(Column):
    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]) -> assets.Column:
        column = super().parse_obj(obj)

        if not column.custom_attributes:
            column.custom_attributes = {}

        if obj.get("numeric_precision_radix", "") != "":
            column.custom_attributes["num_prec_radix"] = obj.get(
                "numeric_precision_radix", ""
            )
        if obj.get("is_identity", "") != "":
            column.custom_attributes["is_identity"] = obj.get("is_identity", "")
        if obj.get("identity_cycle", "") != "":
            column.custom_attributes["identity_cycle"] = obj.get("identity_cycle", "")

        if obj.get("constraint_type", "") == "PRIMARY KEY":
            column.is_primary = True

        elif obj.get("constraint_type", "") == "FOREIGN KEY":
            column.is_foreign = True

        return column


class PostgresAtlasTransformer(AtlasTransformer):
    def __init__(self, connector_name: str, tenant_id: str, **kwargs: Any):
        super().__init__(connector_name, tenant_id, **kwargs)

        self.entity_class_definitions["TABLE"] = PostgresTable
        self.entity_class_definitions["COLUMN"] = PostgresColumn
        self.entity_class_definitions["EXTRAS-PROCEDURE"] = Procedure
