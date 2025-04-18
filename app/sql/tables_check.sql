/*
 * File: tables_check.sql
 * Purpose: Counts accessible tables matching filter criteria
 * 
 * Parameters:
 *   {normalized_exclude_regex} - Regex pattern for schemas to exclude
 *   {normalized_include_regex} - Regex pattern for schemas to include
 *   {temp_table_regex_sql} - Optional SQL for filtering temporary tables
 *
 * Returns: Count of tables/views matching the specified criteria
 *
 * Notes:
 *   - Used for validation and performance estimation
 *   - Includes only tables of types: 'r','p','v','m','f' (regular, partitioned, view, materialized view, foreign)
 *   - Excludes system schemas
 */
SELECT count(*)
FROM pg_class C
LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
WHERE concat(current_database(), concat('.', N.nspname)) !~ '{normalized_exclude_regex}'
    AND concat(current_database(), concat('.', N.nspname)) ~ '{normalized_include_regex}'
    AND N.nspname NOT IN ('performance_schema', 'information_schema') AND N.nspname NOT LIKE 'pg$_%' ESCAPE '$'
    AND C.relkind IN ('r','p','v','m','f')
    {temp_table_regex_sql}