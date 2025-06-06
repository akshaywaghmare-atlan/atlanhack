/*
 * File: filter_metadata.sql
 * Purpose: Retrieves basic schema information for metadata filtering
 *
 * This query returns a list of schema names from the current catalog,
 * excluding system schemas. Used for initial metadata discovery and filtering.
 *
 * Returns:
 *   - Catalog name
 *   - Schema names
 *
 * Notes:
 *   - Uses Trino's information_schema
 */
SELECT DISTINCT
    table_catalog AS catalog_name,
    table_schema AS schema_name
FROM information_schema.tables
