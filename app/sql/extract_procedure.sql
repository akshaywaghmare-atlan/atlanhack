/*
 * File: extract_procedure.sql
 * Purpose: Extracts stored procedure metadata from Trino catalog
 *
 * Returns:
 *   - Procedure metadata including:
 *     - Procedure schema and name
 *     - Procedure definition (if available)
 */
SELECT
    CURRENT_CATALOG AS PROCEDURE_CATALOG,
    r.routine_schema AS PROCEDURE_SCHEMA,
    r.routine_name AS PROCEDURE_NAME,
    NULL AS SOURCE_OWNER,
    r.routine_definition AS procedure_definition,
    r.routine_type AS procedure_type
FROM information_schema.routines r
WHERE r.routine_schema != 'information_schema'