/*
 * File: client_version.sql
 * Purpose: Retrieves PostgreSQL server version information
 * 
 * This query returns the full version string of the connected PostgreSQL server,
 * including version number, platform, and build information.
 *
 * Returns: Server version string
 *
 * Example output: "PostgreSQL 14.5 on x86_64-pc-linux-gnu, compiled by gcc, 64-bit"
 */
SELECT version();