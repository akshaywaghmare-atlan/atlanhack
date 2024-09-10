from dataclasses import dataclass

@dataclass
class WorkflowConfig:
    workflowId: str
    credentialsGUID: str
    className: str
    url: str
    extraPropertiesStr: str
    runtimePropertiesStr: str
    includeFilterStr: str
    excludeFilterStr: str
    fetchColumns: bool
    fetchPrimaryKeys: bool
    fetchImportedKeys: bool
    useJDBCInternalMethods: bool
    systemDatabaseRegexStr: str
    systemSchemaRegexStr: str
    tempTableRegexStr: str
    includeTableRegexStr: str
    outputType: str
    outputPrefix: str
    verbose: bool
    useSourceSchemaFiltering: bool
    tableCompanionSQL: str
    columnCompanionSQL: str
    schemaCompanionSQL: str
    databaseCompanionSQL: str
    extraCompanionSQLs: str
    unfilteredExtraCompanionSQLs: str

