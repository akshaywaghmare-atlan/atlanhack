SELECT count(*)
FROM pg_class C
LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
WHERE concat(current_database(), concat('.', N.nspname)) !~ '{normalized_exclude_regex}'
    AND concat(current_database(), concat('.', N.nspname)) ~ '{normalized_include_regex}'
    AND N.nspname NOT IN ('performance_schema', 'information_schema') AND N.nspname NOT LIKE 'pg$_%' ESCAPE '$'
    AND C.relkind IN ('r','p','v','m','f')
    {temp_table_regex_sql}