/*
 * File: extract_database.sql
 * Purpose: Extracts basic database metadata from the current Trino catalog
 *
 * This query retrieves fundamental catalog information from Trino's
 * system tables.
 *
 * Returns:
 *   - Catalog metadata including name and schema count
 */
SELECT 
    catalog_name,
    catalog_name as database_name,
    (SELECT COUNT(*) FROM information_schema.schemata) as schema_count
FROM information_schema.catalogs 
WHERE catalog_name = CURRENT_CATALOG;