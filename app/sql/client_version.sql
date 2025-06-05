/*
 * File: client_version.sql
 * Purpose: Retrieves Trino server version information
 *
 * This query returns the full version string of the connected Trino server,
 * including version number.
 *
 * Returns: Server version string
 */
SELECT version();