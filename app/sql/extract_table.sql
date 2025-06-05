/*
 * File: extract_table.sql
 * Purpose: Extracts table metadata from Trino catalog
 *
 * Returns:
 *   - Table metadata including:
 *     - Table name, schema, and type
 *     - Column count
 *     - View definition (if applicable)
 */
SELECT
    CURRENT_CATALOG as table_catalog,
    t.table_schema,
    t.table_name,
    t.table_type,
    (
        SELECT COUNT(*)
        FROM information_schema.columns c
        WHERE c.table_schema = t.table_schema
        AND c.table_name = t.table_name
    ) as column_count,
    CASE 
        WHEN t.table_type = 'VIEW' THEN (
            SELECT view_definition 
            FROM information_schema.views v 
            WHERE v.table_schema = t.table_schema 
            AND v.table_name = t.table_name
        )
        ELSE NULL 
    END as view_definition,
    NULL as table_owner,
    NULL as remarks,
    NULL as table_type_cat,
    NULL as self_referencing_col_name,
    NULL as ref_generation,
    NULL as partition_strategy,
    NULL as partition_column_name,
    NULL as is_external,
    NULL as is_temporary,
    NULL as tablespace,
    NULL as options,
    NULL as buffer_pool,
    NULL as table_size_in_bytes,
    NULL as retention_time_in_ms
FROM information_schema.tables t
WHERE t.table_schema != 'information_schema'
ORDER BY t.table_schema, t.table_name