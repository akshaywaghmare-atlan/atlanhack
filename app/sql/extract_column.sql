/*
 * File: extract_column.sql
 * Purpose: Extracts detailed column metadata from PostgreSQL database
 *
 * Parameters:
 *   {normalized_exclude_regex} - Regex pattern for schemas to exclude
 *   {normalized_include_regex} - Regex pattern for schemas to include
 *   {temp_table_regex_sql} - Optional SQL for filtering temporary tables
 *
 * Returns:
 *   - Comprehensive column metadata including:
 *     - Column names, data types, and positions
 *     - Nullability and default values
 *     - Auto-increment and identity properties
 *     - Constraint information (primary key, foreign key, etc.)
 *     - Column descriptions/remarks
 *
 * Notes:
 *   - Only includes non-dropped columns with attnum > 0
 *   - Excludes system schemas
 *   - Complex type handling with special cases for various data types
 *   - Includes constraint types and names for each column
 *   - Results ordered by schema, table, and column position
 */
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
    NULL AS PARTITION_ORDER,  -- Simplified for older versions
    NULL AS IS_PARTITION, -- Added for compatibility with Atlas transformer
    NULL AS NUMERIC_SCALE, -- Added for compatibility with Atlas transformer
    0 AS MAX_LENGTH, -- Added for compatibility with Atlas transformer
    NULL AS IS_SELF_REFERENCING -- Added for compatibility with Atlas transformer

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