from typing import Any, Dict, Union

from application_sdk.transformers.atlas import AtlasTransformer
from application_sdk.transformers.atlas.sql import Table
from application_sdk.transformers.common.utils import build_atlas_qualified_name
from pyatlan.model import assets


class PostgresTable(Table):
    @classmethod
    def parse_obj(
        cls, obj: Dict[str, Any]
    ) -> Union[
        assets.Table, assets.View, assets.MaterialisedView, assets.SnowflakeDynamicTable
    ]:
        """
        Postgres view and materialized view definitions are select queries,
        so we need to format the view definition to be a valid SQL query.

        src: https://github.com/atlanhq/marketplace-packages/blob/master/packages/atlan/postgres/transformers/view.jinja2
        """
        if obj.get("table_type") == "VIEW":
            view_definition = "CREATE OR REPLACE VIEW {view_name} AS {query}"
            obj["view_definition"] = view_definition.format(
                view_name=obj["table_name"], query=obj["view_definition"]
            )
        elif obj.get("table_type") == "MATERIALIZED VIEW":
            view_definition = (
                "CREATE OR REPLACE MATERIALIZED VIEW {view_name} AS {query}"
            )
            obj["view_definition"] = view_definition.format(
                view_name=obj["table_name"], query=obj["view_definition"]
            )

        return super().parse_obj(obj)


# TODO: move this to application_sdk
class Procedure(assets.Procedure):
    """Procedure entity transformer for Atlas.

    This class handles the transformation of procedure metadata into Atlas Procedure entities.
    """

    @classmethod
    def parse_obj(cls, obj: Dict[str, Any]) -> assets.Procedure:
        try:
            procedure = assets.Procedure.creator(
                name=obj["procedure_name"],
                definition=obj["procedure_definition"],
                schema_qualified_name=build_atlas_qualified_name(
                    obj["connection_qualified_name"],
                    obj["procedure_catalog"],
                    obj["procedure_schema"],
                ),
                schema_name=obj["procedure_schema"],
                database_name=obj["procedure_catalog"],
                database_qualified_name=build_atlas_qualified_name(
                    obj["connection_qualified_name"],
                    obj["procedure_catalog"],
                ),
                connection_qualified_name=obj["connection_qualified_name"],
            )
            return procedure
        except AssertionError as e:
            raise ValueError(f"Error creating Table Entity: {str(e)}")


class PostgresAtlasTransformer(AtlasTransformer):
    def __init__(self, connector_name: str, tenant_id: str, **kwargs: Any):
        super().__init__(connector_name, tenant_id, **kwargs)

        self.entity_class_definitions["TABLE"] = PostgresTable
        self.entity_class_definitions["VIEW"] = PostgresTable
        self.entity_class_definitions["MATERIALIZED VIEW"] = PostgresTable
        self.entity_class_definitions["PROCEDURE"] = Procedure
