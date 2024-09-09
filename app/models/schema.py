import json
from pydantic import BaseModel, Field, ConfigDict
from typing import Any

class BaseSchemaModel(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={
            # Add any custom type encoders here if needed
        }
    )

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        kwargs.setdefault('by_alias', True)
        return super().model_dump(*args, **kwargs)

    def json(self, *args, **kwargs) -> str:
        kwargs.setdefault('by_alias', True)
        return super().model_dump_json(*args, **kwargs)


class Namespace(BaseSchemaModel):
    id: str = "postgresql-internal"
    name: str = "postgresql-internal"
    version: int = 1


class Package(BaseSchemaModel):
    id: str = "postgresql-internal"
    name: str = "postgresql-internal"
    version: int = 1


class BaseObjectEntity(BaseSchemaModel):
    typeName: str
    name: str
    URI: str
    sourceVersion: int = 1
    internalVersion: int = 1


## Database

class DatabaseEntity(BaseObjectEntity):
    namespace: Namespace = Field(default_factory=Namespace)
    package: Package = Field(default_factory=Package)


## Schema

class SchemaEntity(BaseObjectEntity):
    namespace: Namespace = Field(default_factory=Namespace)
    package: Package = Field(default_factory=Package)


## Table

class TableEntity(BaseObjectEntity):
    isPartition: bool
    isSearchable: bool = True
    namespace: Namespace = Field(default_factory=Namespace)
    package: Package = Field(default_factory=Package)

## Column

class ColumnConstraint(BaseSchemaModel):
    notNull: bool = False
    autoIncrement: bool = False
    primaryKey: bool = False
    uniqueKey: bool = False


class ColumnEntity(BaseObjectEntity):
    order: int
    dataType: str
    constraints: ColumnConstraint = Field(default_factory=ColumnConstraint)
    isSearchable: bool = True
    namespace: Namespace = Field(default_factory=Namespace)
    package: Package = Field(default_factory=Package)


class PydanticJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        return super().default(obj)