SELECT
    current_database() AS CATALOG_NAME,
    N.nspname AS SCHEMA_NAME,
    S.schema_owner,
    table_counts.table_count,
    table_counts.views_count
FROM pg_catalog.pg_namespace N
LEFT JOIN
	(
	Select
		C.relnamespace,
	 	SUM(CASE WHEN C.relkind IN ('r', 'p', 'f') THEN 1 ELSE 0 END) as table_count,
		SUM(CASE WHEN C.relkind IN ('m', 'v') THEN 1 ELSE 0 END) as views_count
	FROM pg_class C
	GROUP BY C.relnamespace
) as table_counts
ON (table_counts.relnamespace = N.oid)
LEFT JOIN information_schema.schemata S ON S.schema_name = N.nspname
WHERE
    N.nspname NOT LIKE 'pg$_%' ESCAPE '$' AND N.nspname != 'information_schema'
    AND concat(current_database(), concat('.', N.nspname)) !~ '{normalized_exclude_regex}'
    AND concat(current_database(), concat('.', N.nspname)) ~ '{normalized_include_regex}'
ORDER BY N.nspname;