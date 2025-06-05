/*
 * File: extract_column.sql
 * Purpose: Extracts detailed column metadata from Trino catalog
 *
 * Returns:
 *   - Column metadata including:
 *     - Column names, data types, and positions
 *     - Nullability
 *     - Comments (if available)
 */
SELECT
    CURRENT_CATALOG as TABLE_CATALOG,
    c.table_schema as TABLE_SCHEMA,
    c.table_name as TABLE_NAME,
    c.column_name as COLUMN_NAME,
    c.ordinal_position as ORDINAL_POSITION,
    c.data_type as DATA_TYPE,
    c.is_nullable as IS_NULLABLE,
    NULL as COLUMN_DEFAULT,
    NULL as CHARACTER_MAXIMUM_LENGTH,
    NULL as NUMERIC_PRECISION,
    NULL as NUMERIC_SCALE,
    NULL as DATETIME_PRECISION,
    NULL as CHARACTER_SET_NAME,
    NULL as COLLATION_NAME,
    NULL as DOMAIN_CATALOG,
    NULL as DOMAIN_SCHEMA,
    NULL as DOMAIN_NAME,
    NULL as UDT_CATALOG,
    NULL as UDT_SCHEMA,
    NULL as UDT_NAME,
    NULL as SCOPE_CATALOG,
    NULL as SCOPE_SCHEMA,
    NULL as SCOPE_NAME,
    NULL as MAXIMUM_CARDINALITY,
    NULL as DTD_IDENTIFIER,
    NULL as IS_SELF_REFERENCING,
    NULL as IS_IDENTITY,
    NULL as IDENTITY_GENERATION,
    NULL as IDENTITY_START,
    NULL as IDENTITY_INCREMENT,
    NULL as IDENTITY_MAXIMUM,
    NULL as IDENTITY_MINIMUM,
    NULL as IDENTITY_CYCLE,
    NULL as IS_GENERATED,
    NULL as GENERATION_EXPRESSION,
    NULL as IS_UPDATABLE,
    NULL as CONSTRAINT_TYPE,
    NULL as CONSTRAINT_NAME,
    NULL as REMARKS,
    NULL as PARTITION_ORDER,
    NULL as IS_PARTITION,
    NULL as MAX_LENGTH
FROM information_schema.columns c
JOIN information_schema.tables t 
    ON c.table_catalog = t.table_catalog 
    AND c.table_schema = t.table_schema 
    AND c.table_name = t.table_name
WHERE t.table_schema != 'information_schema'
ORDER BY 
    c.table_schema, 
    c.table_name, 
    c.ordinal_position;