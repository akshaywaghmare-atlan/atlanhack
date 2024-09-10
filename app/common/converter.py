from app.models.schema import (
    BaseObjectEntity,
    DatabaseEntity,
    SchemaEntity,
    TableEntity,
    ViewEntity,
    ColumnEntity,
    ColumnConstraint,
)


def transform_metadata(typename: str, data: dict):
    if typename.upper() == "DATABASE":
        try:
            assert data["datname"] is not None, "Database name cannot be None"
            return DatabaseEntity(
                typeName="DATABASE",
                name=data["datname"],
                URI=f"/postgres/sql/{data['datname']}",
            )
        except AssertionError as e:
            print(f"Error creating DatabaseEntity: {str(e)}")
            return None

    elif typename.upper() == "SCHEMA":
        try:
            assert data["schema_name"] is not None, "Schema name cannot be None"
            assert data["catalog_name"] is not None, "Catalog name cannot be None"
            return SchemaEntity(
                typeName="SCHEMA",
                name=data["schema_name"],
                URI=f"/postgres/sql/{data['catalog_name']}/{data['schema_name']}",
            )
        except AssertionError as e:
            print(f"Error creating SchemaEntity: {str(e)}")
            return None

    elif typename.upper() == "TABLE":
        try:
            assert data["table_name"] is not None, "Table name cannot be None"
            assert data["table_cat"] is not None, "Table catalog cannot be None"
            assert data["table_schem"] is not None, "Table schema cannot be None"

            if data["table_type"] == "VIEW":
                return ViewEntity(
                    typeName="VIEW",
                    name=data["table_name"],
                    URI=f"/postgres/sql/{data['table_cat']}/{data['table_schem']}/{data['table_name']}",
                )
            else:
                return TableEntity(
                    typeName="TABLE",
                    name=data["table_name"],
                    URI=f"/postgres/sql/{data['table_cat']}/{data['table_schem']}/{data['table_name']}",
                    isPartition=data.get("is_partition") or False,
                )
        except AssertionError as e:
            print(f"Error creating TableEntity: {str(e)}")
            return None

    elif typename.upper() == "COLUMN":
        try:
            assert data["column_name"] is not None, "Column name cannot be None"
            assert data["table_cat"] is not None, "Table catalog cannot be None"
            assert data["table_schem"] is not None, "Table schema cannot be None"
            assert data["table_name"] is not None, "Table name cannot be None"
            assert (
                data["ordinal_position"] is not None
            ), "Ordinal position cannot be None"
            assert data["data_type"] is not None, "Data type cannot be None"

            return ColumnEntity(
                typeName="COLUMN",
                name=data["column_name"],
                URI=f"/postgres/sql/{data['table_cat']}/{data['table_schem']}/{data['table_name']}/{data['column_name']}",
                order=data["ordinal_position"],
                dataType=data["data_type"],
                constraints=ColumnConstraint(
                    notNull=not data.get("is_nullable") == "NO",
                    autoIncrement=data.get("IS_AUTOINCREMENT") == "YES",
                ),
            )
        except AssertionError as e:
            print(f"Error creating ColumnEntity: {str(e)}")
            return None

    else:
        print(f"Unknown typename: {typename}")
        name = data[f"{typename.lower()}_name"]
        return BaseObjectEntity(
            typeName=typename.upper(),
            name=name,
            URI=f"/postgres/sql/{name}",
        )
