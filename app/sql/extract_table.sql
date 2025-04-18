/*
 * File: extract_table.sql
 * Purpose: Extracts detailed table and view metadata from PostgreSQL database
 * 
 * Parameters:
 *   {normalized_exclude_regex} - Regex pattern for schemas to exclude
 *   {normalized_include_regex} - Regex pattern for schemas to include
 *   {temp_table_regex_sql} - Optional SQL for filtering temporary tables
 *
 * Returns: 
 *   - Comprehensive table metadata including:
 *     - Table names, schemas, and types (table, view, materialized view)
 *     - Row and column counts
 *     - Partition information (for partitioned tables)
 *     - View definitions
 *     - Table remarks/descriptions
 *
 * Notes:
 *   - Only includes regular tables, partitioned tables, foreign tables, 
 *     views, and materialized views (relkind IN ('r','p','v','m','f'))
 *   - Excludes system schemas
 *   - Complex row count estimation based on table statistics
 *   - Partition hierarchy information is included
 */
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