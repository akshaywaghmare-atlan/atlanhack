# Queries
TABLES_CHECK_SQL = """
    SELECT count(*)
    FROM INFORMATION_SCHEMA.TABLES
    WHERE concat(TABLE_CATALOG, concat('.', TABLE_SCHEMA)) !~ '{normalized_exclude_regex}'
        AND concat(TABLE_CATALOG, concat('.', TABLE_SCHEMA)) ~ '{normalized_include_regex}'
        AND TABLE_SCHEMA NOT IN ('performance_schema', 'information_schema', 'pg_catalog', 'pg_internal')
        {temp_table_regex_sql}
"""
TABLES_CHECK_TEMP_TABLE_REGEX_SQL = "AND TABLE_NAME !~ '{exclude_table_regex}'"

TEST_AUTHENTICATION_SQL = "SELECT 1;"

FILTER_METADATA_SQL = """
SELECT schema_name, catalog_name
FROM INFORMATION_SCHEMA.SCHEMATA
WHERE schema_name NOT LIKE 'pg_%' AND schema_name != 'information_schema'
"""

### Extraction Queries

DATABASE_EXTRACTION_SQL = """
SELECT d.*, d.datname as database_name FROM pg_database d WHERE datname = current_database();
"""

SCHEMA_EXTRACTION_SQL = """
SELECT
    s.*,
    table_counts.table_count,
    table_counts.views_count
FROM
    information_schema.schemata s
LEFT JOIN (
    select
	    N.nspname as table_schema,
	    SUM(CASE WHEN C.relkind IN ('r', 'p', 'f') THEN 1 ELSE 0 END) as table_count,
	    SUM(CASE WHEN C.relkind IN ('m', 'v') THEN 1 ELSE 0 END) as views_count
    from pg_class as C
    LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
    LEFT JOIN information_schema.tables T ON (C.relname = T.table_name AND N.nspname = T.table_schema) group by N.nspname
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
        current_database() AS TABLE_CATALOG,
        COALESCE(T.table_schema, MV.schemaname) AS TABLE_SCHEMA,
        COALESCE(T.table_name, MV.matviewname) AS TABLE_NAME,
        (CASE
            WHEN c.reltuples < 0 THEN NULL
            WHEN c.relpages = 0 THEN float8 '0'
            ELSE c.reltuples / c.relpages
        END * (pg_relation_size(c.oid) / pg_catalog.current_setting('block_size')::int))::bigint AS ROW_COUNT,
        C.relnatts AS COLUMN_COUNT,
        C.relkind AS TABLE_KIND,
        CASE
            WHEN C.relkind IN ('r', 'p', 'f') THEN 'TABLE'
            WHEN C.relkind = 'v' THEN 'VIEW'
            WHEN C.relkind = 'm' THEN 'MATERIALIZED VIEW'
            ELSE C.relkind::text
        END AS TABLE_TYPE,
        C.relispartition AS IS_PARTITION,
        P.partstrat AS PARTITION_STRATEGY,
        PC.parition_count AS PARTITION_COUNT,
        PARTITION.parent_name AS PARENT_TABLE_NAME,
        PARTITION.parent_table_kind AS PARTITIONED_PARENT_TABLE,
        PARTITION_RANGE.PARTITION_CONSTRAINT AS PARTITION_CONSTRAINT,
        P.partnatts AS NUMBER_COLUMNS_IN_PART_KEY,
        P.partattrs AS COLUMNS_PARTICIPATING_IN_PART_KEY,
        COALESCE(V.definition, MV.definition) AS VIEW_DEFINITION,
        T.self_referencing_column_name AS SELF_REFERENCING_COLUMN_NAME,
        T.reference_generation AS REFERENCE_GENERATION,
        T.user_defined_type_catalog AS USER_DEFINED_TYPE_CATALOG,
        T.user_defined_type_schema AS USER_DEFINED_TYPE_SCHEMA,
        T.user_defined_type_name AS USER_DEFINED_TYPE_NAME,
        T.is_insertable_into AS IS_INSERTABLE_INTO,
        T.is_typed AS IS_TYPED,
        T.commit_action AS COMMIT_ACTION
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
    {temp_table_regex_sql}
    AND C.relkind != 'i'
    AND C.relkind != 'I';
"""
TABLE_EXTRACTION_TEMP_TABLE_REGEX_SQL = "AND T.TABLE_NAME !~ '{exclude_table_regex}'"

COLUMN_EXTRACTION_SQL = """
SELECT
    current_database() AS TABLE_CATALOG,
    n.nspname AS TABLE_SCHEMA,
    c.relname AS TABLE_NAME,
    a.attname AS COLUMN_NAME,
    a.attnum AS ORDINAL_POSITION,
    pg_get_expr(d.adbin, d.adrelid) AS COLUMN_DEF,
    CASE
        WHEN a.attnotnull THEN 'NO'
        ELSE 'YES'
    END AS IS_NULLABLE,
    format_type(a.atttypid, a.atttypmod) AS DATA_TYPE,
    CASE
        WHEN pg_get_expr(d.adbin, d.adrelid) LIKE 'nextval%' THEN 'YES'
        ELSE 'NO'
    END AS IS_AUTOINCREMENT,
    CASE
        WHEN t.typtype = 'd' THEN t.typtypmod
        ELSE NULL
    END AS NUMERIC_PRECISION,
    CASE
        WHEN t.typtype = 'b' AND t.typelem <> 0 THEN t.typlen
        ELSE NULL
    END AS CHARACTER_OCTET_LENGTH,
    'NEVER' AS IS_GENERATEDCOLUMN,  -- Simplified for older versions
    'NO' AS IS_IDENTITY,  -- Simplified for older versions
    NULL AS IDENTITY_CYCLE,  -- Simplified for older versions
    CASE
        WHEN t.typelem <> 0 THEN t.typelem
        ELSE t.oid
    END::regtype::text AS COLUMN_SIZE,
    2 AS NUM_PREC_RADIX,
    CASE
        WHEN t.typtype = 'b' AND t.typelem = 0 THEN
            CASE
                WHEN t.typname IN ('float4', 'float8') THEN NULL
                ELSE information_schema._pg_numeric_precision(t.oid, -1)
            END
        ELSE NULL
    END AS DECIMAL_DIGITS,
    CASE
        WHEN c.relkind IN ('r', 'p', 'f') THEN 'TABLE'
        WHEN c.relkind = 'v' THEN 'VIEW'
        WHEN c.relkind = 'm' THEN 'MATERIALIZED VIEW'
        ELSE c.relkind::text
    END AS TABLE_TYPE,
    false AS BELONGS_TO_PARTITION,  -- Simplified for older versions
    false AS PARTITIONED_TABLE,  -- Simplified for older versions
    CASE
        WHEN con.contype = 'p' THEN 'PRIMARY KEY'
        WHEN con.contype = 'f' THEN 'FOREIGN KEY'
        WHEN con.contype = 'u' THEN 'UNIQUE'
        WHEN con.contype = 'c' THEN 'CHECK'
        WHEN con.contype = 't' THEN 'TRIGGER'
        WHEN con.contype = 'x' THEN 'EXCLUDE'
        ELSE NULL
    END AS CONSTRAINT_TYPE,
    con.conname AS CONSTRAINT_NAME,
    NULL AS PARTITION_ORDER  -- Simplified for older versions
FROM
    pg_catalog.pg_attribute a
JOIN
    pg_catalog.pg_class c ON c.oid = a.attrelid
JOIN
    pg_catalog.pg_namespace n ON n.oid = c.relnamespace
JOIN
    pg_catalog.pg_type t ON a.atttypid = t.oid
LEFT JOIN
    pg_catalog.pg_attrdef d ON (a.attrelid, a.attnum) = (d.adrelid, d.adnum)
LEFT JOIN
    pg_catalog.pg_constraint con ON (con.conrelid = c.oid AND a.attnum = ANY(con.conkey))
WHERE
    a.attnum > 0
    AND NOT a.attisdropped
    AND n.nspname NOT LIKE 'pg_%%'
    AND n.nspname != 'information_schema'
    AND concat(current_database(), concat('.', n.nspname)) !~ '{normalized_exclude_regex}'
    AND concat(current_database(), concat('.', n.nspname)) ~ '{normalized_include_regex}'
    {temp_table_regex_sql}
    -- ignore relational views (src: https://www.postgresql.org/docs/current/catalog-pg-class.html)
    AND c.reltype != 0
ORDER BY
    n.nspname, c.relname, a.attnum;
"""
COLUMN_EXTRACTION_TEMP_TABLE_REGEX_SQL = "AND c.relname !~ '{exclude_table_regex}'"

PROCEDURE_EXTRACTION_SQL = """
SELECT
        current_database() AS PROCEDURE_CATALOG,
        N.nspname          AS PROCEDURE_SCHEMA,
        P.proname          AS PROCEDURE_NAME,
        B.usename          AS SOURCE_OWNER,
        P.prosrc           AS procedure_definition
    FROM  pg_catalog.pg_namespace N
        JOIN pg_catalog.pg_proc P ON pronamespace = N.oid
        JOIN pg_user B ON B.usesysid = P.proowner
    WHERE nspname NOT IN ('information_schema', 'pg_catalog')
    AND B.usename != 'rdsdb'
    AND concat(current_database(), concat('.', N.nspname)) !~ '{normalized_exclude_regex}'
    AND  concat(current_database(), concat('.', N.nspname)) ~ '{normalized_include_regex}';
"""
