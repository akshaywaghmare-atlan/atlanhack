/*
 * File: filter_metadata.sql
 * Purpose: Retrieves basic schema information for metadata filtering
 *
 * This query returns a list of schema names from the current database,
 * excluding system schemas. Used for initial metadata discovery and filtering.
 *
 * Returns:
 *   - Catalog name (database name)
 *   - Schema names
 *
 * Notes:
 *   - Excludes system schemas (pg_* and information_schema)
 */
SELECT
    current_database() AS CATALOG_NAME,
    N.nspname AS SCHEMA_NAME
FROM pg_namespace N
WHERE N.nspname NOT LIKE 'pg$_%' ESCAPE '$' AND N.nspname != 'information_schema'