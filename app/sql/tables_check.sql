/*
 * File: tables_check.sql
 * Purpose: Counts accessible tables matching filter criteria
 *
 * Returns: Count of tables/views matching the specified criteria
 *
 * Notes:
 *   - Used for validation and performance estimation
 *   - Includes tables and views from all accessible catalogs and schemas
 *   - Excludes system schemas
 */
SELECT count(*) as count
FROM information_schema.tables t
WHERE t.table_schema != 'information_schema'