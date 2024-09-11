from pydantic import BaseModel, Field

from app.dto.credentials import CredentialPayload


class WorkflowConfig(BaseModel):
    workflowId: str
    credentialsGUID: str
    defaultDatabaseName: str = ""
    defaultSchemaName: str = ""
    includeFilterStr: str = "{}"
    excludeFilterStr: str = "{}"
    hasDatabaseAbstraction: bool = False
    augmentTableTypes: bool = False
    useJDBCInternalMethods: bool = True
    fetchPrimaryKeys: bool = True
    fetchImportedKeys: bool = True
    fetchColumns: bool = True
    systemDatabaseRegexStr: str = "[]"
    systemSchemaRegexStr: str = "[]"
    tempTableRegexStr: str = "[]"
    includeTableRegexStr: str = "[]"
    outputType: str = "JSON"
    outputPrefix: str = "/tmp/metadata"
    outputPath: str = "/tmp/metadata/workflowId/runId"
    verbose: bool = False
    useSourceSchemaFiltering: bool = False
    aws_sts_session_duration_seconds: int = 3600
    aws_sts_session_name: str = "atlan_jdbc_metadata_extractor"
    databaseFilterSQL: str = "{}"
    schemaFilterSQL: str = "{}"
    tableFilterSQL: str = ""
    unfilteredExtraCompanionSQLs: str = "{}"
    dynamicQueryJSON: str = "{}"
    excludeTableTypes: str = "[]"
    columnFilterSQL: str = ""
    chunkSize: int = -1


class MetadataConfig(BaseModel):
    exclude_filter: str = Field(default="", alias="exclude-filter")
    include_filter: str = Field(default="", alias="include-filter")
    temp_table_regex: str = Field(default="", alias="temp-table-regex")
    advanced_config_strategy: str = Field(
        default="default", alias="advanced-config-strategy"
    )
    use_source_schema_filtering: str = Field(
        default="false", alias="use-source-schema-filtering"
    )
    use_jdbc_internal_methods: str = Field(
        default="true", alias="use-jdbc-internal-methods"
    )
    authentication: str
    extraction_method: str = Field(alias="extraction-method")

    class Config:
        populate_by_name = True


class ConnectionConfig(BaseModel):
    connection: str


class WorkflowRequestPayload(BaseModel):
    credentials: CredentialPayload = Field(alias="credentials")
    connection: ConnectionConfig
    metadata: MetadataConfig

    class Config:
        populate_by_name = True


class ExtractionConfig(BaseModel):
    workflowConfig: WorkflowConfig
    typename: str
    query: str
