SELECT
    current_database() AS CATALOG_NAME,
    N.nspname AS SCHEMA_NAME
FROM pg_namespace N
WHERE N.nspname NOT LIKE 'pg$_%' ESCAPE '$' AND N.nspname != 'information_schema'