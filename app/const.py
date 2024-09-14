# Constants shared across the application

METADATA_EXTRACTION_TASK_QUEUE = "POSTGRES_METADATA_EXTRACTION_TASK_QUEUE"

# Queries
TABLES_CHECK_SQL = """
    SELECT count(*)
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_NAME !~ '{exclude_table}'
        AND concat(TABLE_CATALOG, concat('.', TABLE_SCHEMA)) !~ '{normalized_exclude_regex}'
        AND concat(TABLE_CATALOG, concat('.', TABLE_SCHEMA)) ~ '{normalized_include_regex}'
        AND TABLE_SCHEMA NOT IN ('performance_schema', 'information_schema', 'pg_catalog', 'pg_internal')
"""

TEST_AUTHENTICATION_SQL = "SELECT 1;"

FILTER_METADATA_SQL = """
SELECT schema_name, catalog_name
FROM INFORMATION_SCHEMA.SCHEMATA
WHERE schema_name NOT LIKE 'pg_%' AND schema_name != 'information_schema'
"""

### Extraction Queries

DATABASE_EXTRACTION_SQL = """
SELECT * FROM pg_database WHERE datname = current_database();
"""

SCHEMA_EXTRACTION_SQL = """
SELECT
    s.*,
    table_counts.table_count,
    table_counts.view_count,
    table_counts.materialized_view_count
FROM
    information_schema.schemata s
LEFT JOIN (
    SELECT
        table_schema,
        SUM(CASE WHEN table_type = 'BASE TABLE' THEN 1 ELSE 0 END) as table_count,
        SUM(CASE WHEN table_type = 'VIEW' THEN 1 ELSE 0 END) as view_count,
        SUM(CASE WHEN table_type = 'MATERIALIZED VIEW' THEN 1 ELSE 0 END) as materialized_view_count
    FROM
        information_schema.tables
    GROUP BY
        table_schema
) as table_counts
ON s.schema_name = table_counts.table_schema
WHERE
    s.schema_name NOT LIKE 'pg_%'
    AND s.schema_name != 'information_schema'
    AND concat(s.CATALOG_NAME, concat('.', s.SCHEMA_NAME)) !~ '{normalized_exclude_regex}'
    AND concat(s.CATALOG_NAME, concat('.', s.SCHEMA_NAME)) ~ '{normalized_include_regex}';
"""

TABLE_EXTRACTION_SQL = """
    SELECT
        current_database() AS TABLE_CAT,
        COALESCE(T.table_schema, MV.schemaname) AS TABLE_SCHEM,
        COALESCE(T.table_name, MV.matviewname) AS TABLE_NAME,
        (CASE
            WHEN c.reltuples < 0 THEN NULL
            WHEN c.relpages = 0 THEN float8 '0'
            ELSE c.reltuples / c.relpages
        END * (pg_relation_size(c.oid) / pg_catalog.current_setting('block_size')::int))::bigint AS ROW_COUNT,
        C.relnatts AS COLUMN_COUNT,
        C.relkind AS TABLE_KIND,
        C.relispartition AS IS_PARTITION,
        P.partstrat AS PARTITION_STRATEGY,
        PC.parition_count AS PARTITION_COUNT,
        PARTITION.parent_name AS PARENT_TABLE_NAME,
        PARTITION.parent_table_kind AS PARTITIONED_PARENT_TABLE,
        PARTITION_RANGE.PARTITION_CONSTRAINT AS PARTITION_CONSTRAINT,
        P.partnatts AS NUMBER_COLUMNS_IN_PART_KEY,
        P.partattrs AS COLUMNS_PARTICIPATING_IN_PART_KEY,
        COALESCE(V.definition, MV.definition) AS VIEW_DEFINITION,
        T.*
    FROM pg_class C
    LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
    LEFT JOIN pg_stat_user_tables PSUT ON (C.oid = PSUT.relid)
    LEFT JOIN information_schema.tables T ON (C.relname = T.table_name AND N.nspname = T.table_schema)
    LEFT JOIN pg_views V ON (T.table_name = V.viewname)
    LEFT JOIN pg_matviews MV ON (C.relname = MV.matviewname)
    LEFT JOIN pg_partitioned_table P ON C.oid = P.partrelid
    LEFT JOIN (
        SELECT
            parent.relname AS table_name,
            COUNT(*) AS parition_count
        FROM pg_inherits
        JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
        JOIN pg_class child ON pg_inherits.inhrelid = child.oid
        JOIN pg_namespace nmsp_parent ON nmsp_parent.oid = parent.relnamespace
        JOIN pg_namespace nmsp_child ON nmsp_child.oid = child.relnamespace
        GROUP BY table_name
    ) AS PC ON (C.relname = PC.table_name)
    LEFT JOIN (
        SELECT
            child.relname AS table_name,
            parent.relname AS parent_name,
            parent.relispartition AS parent_table_kind
        FROM pg_inherits
        JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
        JOIN pg_class child ON pg_inherits.inhrelid = child.oid
        JOIN pg_namespace nmsp_parent ON nmsp_parent.oid = parent.relnamespace
        JOIN pg_namespace nmsp_child ON nmsp_child.oid = child.relnamespace
        WHERE parent.relkind = 'p'
    ) AS PARTITION ON (C.relname = PARTITION.table_name)
    LEFT JOIN (
        SELECT
            c.relname AS PARTITION_NAME,
            pg_get_expr(c.relpartbound, c.oid, true) AS PARTITION_CONSTRAINT
        FROM pg_class c
        WHERE c.relispartition = 'true' AND c.relkind = 'r'
    ) AS PARTITION_RANGE ON (C.relname = PARTITION_RANGE.PARTITION_NAME)
    WHERE N.nspname IN (
        SELECT schema_name
        FROM INFORMATION_SCHEMA.SCHEMATA
        WHERE schema_name NOT LIKE 'pg_%%' AND schema_name != 'information_schema'
        AND concat(CATALOG_NAME, concat('.', SCHEMA_NAME)) !~ '{normalized_exclude_regex}'
        AND concat(CATALOG_NAME, concat('.', SCHEMA_NAME)) ~ '{normalized_include_regex}'
    )
    AND T.table_name !~ '{exclude_table}'
    AND C.relkind != 'i'
    AND C.relkind != 'I';
"""


COLUMN_EXTRACTION_SQL = """
SELECT
    current_database() AS TABLE_CAT,
    columns.TABLE_SCHEMA AS TABLE_SCHEM,
    columns.ordinal_position AS ORDINAL_POSITION,
    C.relispartition AS BELONGS_TO_PARTITION,
    CASE
        WHEN C.relkind = 'p' THEN true
        ELSE false
    END AS PARTITIONED_TABLE,
    CASE
        WHEN C.relkind = 'r' THEN 'TABLE'
        WHEN C.relkind = 'v' THEN 'VIEW'
        WHEN C.relkind = 'm' THEN 'MATERIALIZED VIEW'
        ELSE C.relkind::text
    END AS TABLE_TYPE,
    columns.*,
    col_constraints.constraint_type,
    col_constraints.constraint_name
FROM
    information_schema.columns AS columns
LEFT OUTER JOIN (
    SELECT
        tab_constraints.constraint_type,
        col_constraints.constraint_name,
        col_constraints.table_schema,
        col_constraints.table_name,
        col_constraints.column_name
    FROM
        information_schema.key_column_usage AS col_constraints
    INNER JOIN
        information_schema.table_constraints AS tab_constraints
    ON
        col_constraints.table_schema = tab_constraints.table_schema
        AND col_constraints.table_name = tab_constraints.table_name
        AND col_constraints.constraint_name = tab_constraints.constraint_name
) AS col_constraints
ON
    columns.table_schema = col_constraints.table_schema
    AND columns.table_name = col_constraints.table_name
    AND columns.column_name = col_constraints.column_name
INNER JOIN (
    SELECT
        N.nspname,
        C.relname,
        C.relispartition,
        c.relkind
    FROM
        pg_class AS C
    INNER JOIN
        pg_namespace N ON N.oid = C.relnamespace
) AS C
ON
    C.nspname = columns.table_schema
    AND C.relname = columns.table_name
WHERE
    columns.table_schema NOT LIKE 'pg_%%'
    AND columns.table_schema != 'information_schema'
    AND concat(columns.TABLE_CATALOG, concat('.', columns.TABLE_SCHEMA)) !~ '{normalized_exclude_regex}'
    AND  concat(columns.TABLE_CATALOG, concat('.', columns.TABLE_SCHEMA)) ~ '{normalized_include_regex}'
    AND columns.table_name !~ '{exclude_table}';
"""

PROCEDURE_EXTRACTION_SQL = """
SELECT
        current_database() AS TABLE_CAT,
        N.nspname          AS TABLE_SCHEM,
        N.nspname          AS PROCEDURE_SCHEM,
        P.proname          AS PROCEDURE_NAME,
        B.usename          AS PROC_OWNER,
        P.prosrc           AS ROUTINE_DEFINITION
    FROM  pg_catalog.pg_namespace N
        JOIN pg_catalog.pg_proc P ON pronamespace = N.oid
        JOIN pg_user B ON B.usesysid = P.proowner
    WHERE nspname NOT IN ('information_schema', 'pg_catalog')
    AND B.usename != 'rdsdb'
    AND concat(current_database(), concat('.', N.nspname)) !~ '{normalized_exclude_regex}'
    AND  concat(current_database(), concat('.', N.nspname)) ~ '{normalized_include_regex}';
"""
