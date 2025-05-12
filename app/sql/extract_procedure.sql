/*
 * File: extract_procedure.sql
 * Purpose: Extracts stored procedure metadata from PostgreSQL database
 *
 * Parameters:
 *   {normalized_exclude_regex} - Regex pattern for schemas to exclude
 *   {normalized_include_regex} - Regex pattern for schemas to include
 *
 * Returns:
 *   - Procedure metadata including:
 *     - Procedure schema and name
 *     - Source owner (creator)
 *     - Procedure definition (source code)
 *
 * Notes:
 *   - Excludes system schemas (information_schema, pg_catalog)
 *   - Excludes system procedures (rdsdb user)
 *   - Results filtered by include/exclude regex patterns
 */
SELECT
    current_database() AS PROCEDURE_CATALOG,
    N.nspname          AS PROCEDURE_SCHEMA,
    P.proname          AS PROCEDURE_NAME,
    B.usename          AS SOURCE_OWNER,
    P.prosrc           AS procedure_definition,
    NULL               AS procedure_type
FROM  pg_catalog.pg_namespace N
    JOIN pg_catalog.pg_proc P ON pronamespace = N.oid
    JOIN pg_user B ON B.usesysid = P.proowner
WHERE nspname NOT IN ('information_schema', 'pg_catalog')
AND B.usename != 'rdsdb'
AND concat(current_database(), concat('.', N.nspname)) !~ '{normalized_exclude_regex}'
AND  concat(current_database(), concat('.', N.nspname)) ~ '{normalized_include_regex}';