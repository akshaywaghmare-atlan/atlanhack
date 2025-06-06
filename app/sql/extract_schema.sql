/*
 * File: extract_schema.sql
 * Purpose: Extracts schema metadata from Presto catalog
 *
 * Returns:
 *   - Schema metadata including name and table/view counts
 *
 * Notes:
 *   - Ordered by catalog and schema name
 */
WITH table_counts AS (
    SELECT 
        table_catalog,
        table_schema,
        COUNT(CASE WHEN table_type = 'BASE TABLE' THEN 1 END) as table_count,
        COUNT(CASE WHEN table_type = 'VIEW' THEN 1 END) as views_count
    FROM information_schema.tables
    GROUP BY table_catalog, table_schema
)
SELECT
    s.catalog_name AS CATALOG_NAME,
    s.schema_name AS SCHEMA_NAME,
    NULL as schema_owner,
    COALESCE(tc.table_count, 0) as table_count,
    COALESCE(tc.views_count, 0) as views_count
FROM information_schema.schemata s
LEFT JOIN table_counts tc 
    ON tc.table_catalog = s.catalog_name 
    AND tc.table_schema = s.schema_name
WHERE s.schema_name != 'information_schema'
  AND s.catalog_name IN ('tpcds', 'tpch', 'memory')  -- Filter for specific catalogs
ORDER BY 
    s.catalog_name,
    s.schema_name