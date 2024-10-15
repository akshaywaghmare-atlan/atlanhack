const formConfig = {
    "properties": {
        "host": {
            "type": "string",
            "required": true,
            "default": "",
            "ui": {
                "widget": "text",
                "label": "Host",
                "placeholder": "[database-identifier].[unqiue-identifier].[aws-region].rds.amazonaws.com",
                "feedback": true,
                "help": "Hostname or IP address of the database server.",
                "grid": 8,
            }
        },
        "port": {
            "type": "number",
            "required": true,
            "default": 5432,
            "ui": {
                "widget": "text",
                "label": "Port",
                "placeholder": "Port Number",
                "feedback": true,
                "help": "Port number of the database server.",
                "grid": 4,
            },
        },
        "authentication": {
            "type": "string",
            "enum": ["BASIC", "IAM_USER", "IAM_ROLE"],
            "default": "BASIC",
            "enumNames": ["Basic", "IAM User", "IAM Role"],
            "disabledEnum": ["IAM_ROLE", "IAM_USER"],
            "ui": {
                "widget": "radio",
                "hidden": false,
                "label": "Authentication",
                "grid": 12,
                "rules": [
                    {
                        "required": true,
                        "message": "Please select a valid authentication method"
                    }
                ]
            }
        },
        "user": {
            "type": "string",
            "required": true,
            "default": "postgres",
            "ui": {
                "widget": "text",
                "label": "Username",
                "placeholder": "Username",
                "feedback": true,
                "help": "Username to connect to the database.",
                "grid": 6,
            }
        },
        "password": {
            "type": "string",
            "required": true,
            "default": "",
            "ui": {
                "widget": "password",
                "label": "Password",
                "placeholder": "Password",
                "feedback": true,
                "help": "Password to connect to the database.",
                "grid": 6,
            }
        },
        "database": {
            "type": "string",
            "default": "postgres",
            "required": true,
            "grid": 6,
            "ui": {
                "widget": "text",
                "label": "Database",
                "placeholder": "Database Name",
                "feedback": true,
                "grid": 6,
                "help": "Name of the database to connect to. Defaults to 'postgres'."
            }
        },
        "test-connection": {
            "type": "string",
            "required": false,
            "ui": {
                "widget": "button",
                "label": "Test Connection",
            }
        },
        "cloud-provider": {
            "ui": {
                "widget": "CloudProvider",
                "hidden": true
            }
        },
        "credential_guid": {
        "type": "string",
        "required": true,
        "ui": {
            "widget": "credential",
            "label": "",
            "credentialType": "atlan-connectors-postgres",
            "placeholder": "Credential Guid",
            "hidden": true
        }
        },
        "connection": {
            "type": "string",
            "required": true,
            "ui": {
                "widget": "string",
                "label": "Connection Name",
                "placeholder": "Connection Name",
                "grid": 6,
                "help": "Name of your connection which represents your source environment. Example - 'production', 'development', 'gold', 'analytics'",
                "prefix": {
                    type: 'image',
                    src: 'https://www.postgresql.org/media/img/about/press/elephant.png',
                }
            }
        },
        "publish_mode": {
            "type": "string",
            "enum": ["production", "test", "dev"],
            "default": "production",
            "enumNames": ["Production", "Test", "Development"],
            "ui": {
                "widget": "select",
                "label": "Run Mode",
                "grid": 4,
                "placeholder": "Connection Mode"
            }
        },
        "temp_table_regex": {
            "type": "string",
            "required": false,
            "default": "",
            "ui": {
                "widget": "text",
                "label": "Exclude regex for tables & views",
                "feedback": true,
                "help": "Regex of tables & views to ignore. Defaults to empty string",
                "placeholder": ".*_TMP|.*_TEMP|TMP.*|TEMP.*",
                "grid": 6
            }
        },
        "include_filter": {
            "type": "object",
            "additionalProperties": {
                "type": "array"
            },
            "ui": {
                "widget": "sqltree",
                "sql": "show atlan schemas",
                "credential": "credential-guid",
                "schemaExcludePattern": ["pg_*", "information_*"],
                "label": "Include Metadata",
                "help": "Only the selected databases and schemas will be extracted. Exclude gets preference over include for common databases and schemas, if present, in the config.",
                "grid": 6,
                "placeholder": "Select databases and schemas"
            }
        },
        "exclude_filter": {
            "type": "object",
            "additionalProperties": {
                "type": "array"
            },
            "ui": {
                "widget": "sqltree",
                "sql": "show atlan schemas",
                "credential": "credential-guid",
                "schemaExcludePattern": ["pg_*", "information_*"],
                "label": "Exclude Metadata",
                "help": "Selected databases and schemas wont be extracted.",
                "grid": 6,
                "placeholder": "Select databases and schemas"
            }
        },
        "use_source_schema_filtering": {
            "type": "string",
            "enum": ["true", "false"],
            "default": "false",
            "enumNames": ["True", "False"],
            "disabledEnum": ["false"],
            "ui": {
                "widget": "radio",
                "label": "Enable Source Level Filtering",
                "help": "Enable or Disable Schema Level Filtering on source. Schemas selected in the include filter will be fetched.",
                "hidden": false
            }
        },
        "use_jdbc_internal_methods": {
            "type": "string",
            "enum": ["true", "false"],
            "default": "true",
            "enumNames": ["True", "False"],
            "disabledEnum": ["false"],
            "ui": {
                "widget": "radio",
                "label": "Use JDBC Internal Methods",
                "help": "Enable or Disable JDBC internal methods for data extraction.",
                "hidden": true
            }
        },
        "advanced_config_strategy": {
            "type": "string",
            "enum": ["default", "custom"],
            "default": "default",
            "required": true,
            "enumNames": ["Default", "Custom"],
            "disabledEnum": ["custom"],
            "ui": {
                "widget": "radio",
                "hidden": false,
                "label": "Advanced Config",
                "help": "Controls custom experimental features for the crawler",
                "placeholder": "Advanced Config",
                "rules": [
                    {
                        "required": true,
                        "message": "Please select a valid configuration"
                    }
                ]
            }
        },
        "extraction-method": {
            "type": "string",
            "enum": ["direct", "s3"],
            "default": "direct",
            "enumNames": ["Direct", "Offline"],
            "disabledEnum": ['s3'],
            "ui": {
                "widget": "radio",
                "hidden": false,
                "label": "Extraction method",
                "help": "Determines the method the package will use to extract metadata. 'Direct' means package will directly connect to the database. 'Offline' means package will fetch metadata from bucket.",
                "placeholder": "Direct",
                "rules": [
                {
                    "required": true,
                    "message": "Please select a valid metadata extraction strategy"
                }
                ]
            }
        },
        "preflight-check": {
            "type": "string",
            "ui": {
                "widget": "sage",
                "label": "Preflight Check",
                "config": [
                    {
                        "id": 1,
                        "name": "databaseSchemaCheck",
                        "extraUrlParam": "",
                        "optional": false,
                        "title": "Databases and schemas",
                        "loaderText": "Checking databases/schemas permissions"
                    },
                    {
                        "id": 2,
                        "name": "tablesCheck",
                        "extraUrlParam": "",
                        "optional": false,
                        "title": "Tables",
                        "loaderText": "Checking tables"
                    }
                ],
                "grid": 12,
            }
        },
        "preflight-check-s3": {
            "type": "string",
            "ui": {
                "widget": "sage",
                "config": [
                    {
                        "id": 1,
                        "name": "S3Check",
                        "extraUrlParam": "",
                        "optional": false,
                        "title": "Bucket credentials",
                        "loaderText": "Checking bucket credentials"
                    }
                ]
            }
        },
        "metadata-s3-bucket": {
            "type": "string",
            "required": true,
            "default": "",
            "ui": {
                "hidden": false,
                "label": "Bucket Name",
                "placeholder": "my_bucket_name",
                "feedback": true,
                "help": "Name of the bucket/storage that contains the extracted metadata files.",
                "grid": 4
            }
        },
        "metadata-s3-prefix": {
            "type": "string",
            "required": true,
            "ui": {
                "hidden": false,
                "label": "Bucket Prefix",
                "placeholder": "path_to_file",
                "feedback": true,
                "help": "The prefix is everything after the bucket/storage name, including the `path`.",
                "grid": 4,
                "rules": [
                {
                    "required": true,
                    "message": "Please enter a valid bucket prefix"
                }
                ]
            }
        },
        "metadata-s3-region": {
            "type": "string",
            "required": false,
            "default": "",
            "ui": {
                "hidden": false,
                "label": "Azure Storage Account",
                "placeholder": "region_name",
                "feedback": true,
                "help": "The name azure storage account name (if applicable).",
                "grid": 4
            }
        },
        "blob-sas-token": {
            "type": "string",
            "required": false,
            "default": "",
            "ui": {
                "hidden": true,
                "label": "Blob SAS Token",
                "placeholder": "sas_token",
                "feedback": true,
                "help": "SAS Token for blob. This is required for external azure blob",
                "grid": 4
            }
        }
    },
    "steps": [
        {
            "id": "credential",
            "title": "Credential",
            "description": "Credential Details",
            "properties": [
                "extraction-method",
                "host",
                "port",
                "authentication",
                "user",
                "password",
                "database",
                "test-connection"
            ]
        },
        {
            "id": "connection",
            "title": "Connection",
            "description": "Connection Details",
            "properties": ["connection"],
        },
        {
            "id": "metadata",
            "title": "Metadata",
            "description": "Metadata",
            "properties": [
                "exclude_filter",
                "include_filter",
                "temp_table_regex",
                "advanced_config_strategy",
                "use_source_schema_filtering",
                "use_jdbc_internal_methods",
                "preflight-check",
            ]
        }
    ],
    "ui": {
        "label": "Postgres Assets",
        "publishedBy": "Atlan",
        "type": "CONNECTOR",
        "version": "0.0.1",
        "description": "Package to crawl PostgreSQL assets and publish to Atlan for discovery",
        "documentation": {
            title: 'Postgres Assets Docs',
            link: "https://ask.atlan.com/hc/en-us/articles/6329557275793-How-to-crawl-PostgreSQL"
        },
        "icon": "https://www.postgresql.org/media/img/about/press/elephant.png",
    }
}


export default formConfig