/*
 * File: client_version.sql
 * Purpose: Retrieves Presto server version information
 *
 * This query returns the full version string of the connected Presto server,
 * including version number.
 *
 * Returns: Server version string
 */
SELECT DISTINCT node_version FROM system.runtime.nodes 
