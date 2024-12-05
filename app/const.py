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
        T.commit_action AS COMMIT_ACTION,
        CASE
            WHEN t.table_type = 'BASE TABLE' THEN 'TABLE'
            ELSE t.table_type
        END AS TABLE_TYPE
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
    CASE
        WHEN a.attgenerated = 's' THEN 'STORED'
        WHEN a.attgenerated = 'v' THEN 'VIRTUAL'
        ELSE 'NEVER'
    END AS IS_GENERATEDCOLUMN,
    CASE
        WHEN a.attidentity = 'a' THEN 'YES'
        WHEN a.attidentity = 'd' THEN 'YES'
        ELSE 'NO'
    END AS IS_IDENTITY,
    CASE
        WHEN a.attidentity = 'a' THEN 'YES'
        WHEN a.attidentity = 'd' THEN 'NO'
        ELSE NULL
    END AS IDENTITY_CYCLE,
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
        WHEN c.relkind = 'r' THEN 'TABLE'
        WHEN c.relkind = 'v' THEN 'VIEW'
        WHEN c.relkind = 'm' THEN 'MATERIALIZED VIEW'
        ELSE c.relkind::text
    END AS TABLE_TYPE,
    c.relispartition AS BELONGS_TO_PARTITION,
    CASE WHEN c.relkind = 'p' THEN true ELSE false END AS PARTITIONED_TABLE,
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
    CASE
        WHEN c.relispartition THEN (
            SELECT a.attnum
            FROM pg_attribute a
            JOIN pg_partitioned_table pt ON pt.partrelid = c.oid
            WHERE a.attrelid = c.oid AND a.attnum = ANY(pt.partattrs)
        )
        ELSE NULL
    END AS PARTITION_ORDER
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
    AND c.relname !~ '{exclude_table}'
ORDER BY
    n.nspname, c.relname, a.attnum;
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
