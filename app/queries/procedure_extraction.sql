SELECT
    current_database() AS PROCEDURE_CATALOG,
    N.nspname          AS PROCEDURE_SCHEMA,
    P.proname          AS PROCEDURE_NAME,
    B.usename          AS SOURCE_OWNER,
    P.prosrc           AS procedure_definition
FROM  pg_catalog.pg_namespace N
    JOIN pg_catalog.pg_proc P ON pronamespace = N.oid
    JOIN pg_user B ON B.usesysid = P.proowner
WHERE nspname NOT IN ('information_schema', 'pg_catalog')
AND B.usename != 'rdsdb'
AND concat(current_database(), concat('.', N.nspname)) !~ '{normalized_exclude_regex}'
AND  concat(current_database(), concat('.', N.nspname)) ~ '{normalized_include_regex}';