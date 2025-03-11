# Queries
TABLES_CHECK_SQL = """
    SELECT count(*)
    FROM pg_class C
    LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
    WHERE concat(current_database(), concat('.', N.nspname)) !~ '{normalized_exclude_regex}'
        AND concat(current_database(), concat('.', N.nspname)) ~ '{normalized_include_regex}'
        AND N.nspname NOT IN ('performance_schema', 'information_schema') AND N.nspname NOT LIKE 'pg$_%' ESCAPE '$'
        AND C.relkind IN ('r','p','v','m','f')
        {temp_table_regex_sql}
"""
TABLES_CHECK_TEMP_TABLE_REGEX_SQL = "AND C.relname !~ '{exclude_table_regex}'"

TEST_AUTHENTICATION_SQL = "SELECT 1;"

FILTER_METADATA_SQL = """
SELECT
    current_database() AS CATALOG_NAME,
    N.nspname AS SCHEMA_NAME
FROM pg_namespace N
WHERE N.nspname NOT LIKE 'pg$_%' ESCAPE '$' AND N.nspname != 'information_schema'
"""

### Extraction Queries

DATABASE_EXTRACTION_SQL = """
SELECT d.*, d.datname as database_name FROM pg_database d WHERE datname = current_database();
"""

SCHEMA_EXTRACTION_SQL = """
SELECT
    current_database() AS CATALOG_NAME,
    N.nspname AS SCHEMA_NAME,
    S.schema_owner,
    table_counts.table_count,
    table_counts.views_count
FROM pg_catalog.pg_namespace N
LEFT JOIN
	(
	Select
		C.relnamespace,
	 	SUM(CASE WHEN C.relkind IN ('r', 'p', 'f') THEN 1 ELSE 0 END) as table_count,
		SUM(CASE WHEN C.relkind IN ('m', 'v') THEN 1 ELSE 0 END) as views_count
	FROM pg_class C
	GROUP BY C.relnamespace
) as table_counts
ON (table_counts.relnamespace = N.oid)
LEFT JOIN information_schema.schemata S ON S.schema_name = N.nspname
WHERE
    N.nspname NOT LIKE 'pg$_%' ESCAPE '$' AND N.nspname != 'information_schema'
    AND concat(current_database(), concat('.', N.nspname)) !~ '{normalized_exclude_regex}'
    AND concat(current_database(), concat('.', N.nspname)) ~ '{normalized_include_regex}'
ORDER BY N.nspname;
"""

TABLE_EXTRACTION_SQL = """
    SELECT
        current_database() AS TABLE_CATALOG,
        N.nspname AS TABLE_SCHEMA,
        C.relname AS TABLE_NAME,
        (CASE
            WHEN c.reltuples < 0 THEN NULL
            WHEN c.relpages = 0 THEN float8 '0'
            ELSE c.reltuples / c.relpages
        END * (pg_relation_size(c.oid) / pg_catalog.current_setting('block_size')::int))::bigint AS ROW_COUNT,
        C.relnatts AS COLUMN_COUNT,
        C.relkind AS TABLE_KIND,
        CASE
            WHEN C.relkind = 'r' THEN 'TABLE'
            WHEN C.relkind = 'p' THEN 'PARTITIONED TABLE'
            WHEN C.relkind = 'f' THEN 'FOREIGN TABLE'
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
        T.commit_action AS COMMIT_ACTION,
        D.description AS REMARKS
    FROM pg_class C
    LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
    LEFT JOIN pg_description D ON (C.oid = D.objoid AND D.objsubid = 0  and D.classoid = 'pg_class'::regclass)
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
    WHERE N.nspname NOT LIKE 'pg$_%' ESCAPE '$' AND  N.nspname != 'information_schema'
    AND concat(current_database(), concat('.', N.nspname)) !~ '{normalized_exclude_regex}'
    AND concat(current_database(), concat('.', N.nspname)) ~ '{normalized_include_regex}'
    {temp_table_regex_sql}
    -- ignore indexes, partitioned indexes and sequences
    AND C.relkind IN ('r','p','v','m','f');
"""

TABLE_EXTRACTION_TEMP_TABLE_REGEX_SQL = "AND C.relname !~ '{exclude_table_regex}'"

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
    t.typname AS DATA_TYPE,
    CASE
        WHEN pg_get_expr(d.adbin, d.adrelid) LIKE 'nextval%' THEN 'YES'
        ELSE 'NO'
    END AS IS_AUTO_INCREMENT,
    CASE
        WHEN t.typtype = 'd' THEN t.typtypmod
        ELSE NULL
    END AS NUMERIC_PRECISION,
    CASE
        WHEN t.typtype = 'b' AND t.typelem <> 0 THEN t.typlen
        ELSE NULL
    END AS CHARACTER_OCTET_LENGTH,
    'NO' AS IS_GENERATED,  -- Simplified for older versions
    'NO' AS IS_IDENTITY,  -- Simplified for older versions
    NULL AS IDENTITY_CYCLE,  -- Simplified for older versions
    CASE
        WHEN t.typelem <> 0 THEN t.typelem
        ELSE t.oid
    END::regtype::text AS COLUMN_SIZE,
    CASE
        WHEN t.typname IN ('bit', 'varbit') THEN 2
        ELSE 10
    END AS NUM_PREC_RADIX,
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
        WHEN c.relkind = 'p' THEN 'PARTITIONED TABLE'
        WHEN c.relkind = 'f' THEN 'FOREIGN TABLE'
        WHEN c.relkind = 'v' THEN 'VIEW'
        WHEN c.relkind = 'm' THEN 'MATERIALIZED VIEW'
        ELSE c.relkind::text
    END AS TABLE_TYPE,
    CASE
        WHEN C.relispartition THEN 'YES'
        ELSE 'NO'
    END AS BELONGS_TO_PARTITION,  -- Simplified for older versions
    CASE
        WHEN C.relispartition THEN 'YES'
        ELSE 'NO'
    END AS PARTITIONED_TABLE,  -- Simplified for older versions
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
    ds.description AS REMARKS,
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
LEFT JOIN pg_catalog.pg_description ds
    ON ds.objoid = c.oid AND ds.objsubid = a.attnum
WHERE
    a.attnum > 0
    AND NOT a.attisdropped
    AND n.nspname NOT LIKE 'pg$_%' ESCAPE '$'
    AND n.nspname != 'information_schema'
    AND concat(current_database(), concat('.', n.nspname)) !~ '{normalized_exclude_regex}'
    AND concat(current_database(), concat('.', n.nspname)) ~ '{normalized_include_regex}'
    {temp_table_regex_sql}
    -- ignore relational views (src: https://www.postgresql.org/docs/current/catalog-pg-class.html)
    AND c.reltype != 0
    -- ignore indexes, partitioned indexes and sequences
    AND c.relkind IN ('r','p','v','m','f')
ORDER BY
    n.nspname, c.relname, a.attnum;
"""
COLUMN_EXTRACTION_TEMP_TABLE_REGEX_SQL = "AND c.relname !~ '{exclude_table_regex}'"

# note: that procedures were introduced in postgres 11 and prior to that they were called functions
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
