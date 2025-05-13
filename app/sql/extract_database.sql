/*
 * File: extract_database.sql
 * Purpose: Extracts basic database metadata from the current PostgreSQL database
 *
 * This query retrieves fundamental database information including database name
 * and all associated metadata from the pg_database system catalog.
 *
 * Returns:
 *   - Database metadata including name and system properties
 *
 * Notes:
 *   - Scoped to the current database (current_database())
 */
SELECT d.*, d.datname as database_name, 0 as schema_count FROM pg_database d WHERE datname = current_database();