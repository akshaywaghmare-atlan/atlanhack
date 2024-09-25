import json
import logging
from typing import Any, Dict, List, Set, Tuple

import psycopg2

from app.const import FILTER_METADATA_SQL, TABLES_CHECK_SQL
from sdk.dto.credentials import BasicCredential
from sdk.dto.preflight import PreflightPayload

logger = logging.getLogger(__name__)


class Preflight:
    DATABASE_KEY = "TABLE_CATALOG"
    SCHEMA_KEY = "TABLE_SCHEMA"

    @staticmethod
    def check(payload: PreflightPayload) -> Dict[str, Any]:
        logger.info("Starting preflight check")
        results: Dict[str, Any] = {}
        try:
            results["databaseSchemaCheck"] = Preflight.check_schemas_and_databases(
                payload
            )
            results["tablesCheck"] = Preflight.tables_check(payload)
            logger.info("Preflight check completed successfully")
        except Exception as e:
            logger.error("Error during preflight check", exc_info=True)
            results["error"] = f"Preflight check failed: {str(e)}"
        return results

    @staticmethod
    def fetch_metadata(credentials: BasicCredential) -> List[Dict[str, str]]:
        conn = psycopg2.connect(**credentials.model_dump())
        cursor = conn.cursor()
        cursor.execute(FILTER_METADATA_SQL)

        result: List[Dict[str, str]] = []
        while True:
            rows = cursor.fetchmany(1000)  # Fetch 1000 rows at a time
            if not rows:
                break
            for schema_name, catalog_name in rows:
                result.append(
                    {
                        Preflight.DATABASE_KEY: catalog_name,
                        Preflight.SCHEMA_KEY: schema_name,
                    }
                )
        cursor.close()
        conn.close()
        return result

    @staticmethod
    def check_schemas_and_databases(payload: PreflightPayload) -> Dict[str, Any]:
        logger.info("Starting schema and database check")
        connection = None
        try:
            schemas_results: List[Dict[str, str]] = Preflight.fetch_metadata(
                payload.credentials.get_credential_config()
            )

            include_filter = json.loads(payload.form_data.include_filter)
            allowed_databases, allowed_schemas = Preflight.extract_allowed_schemas(
                schemas_results
            )
            check_success, missing_object_name = Preflight.validate_filters(
                include_filter, allowed_databases, allowed_schemas
            )

            return {
                "success": check_success,
                "successMessage": "Schemas and Databases check successful"
                if check_success
                else "",
                "failureMessage": f"Schemas and Databases check failed for {missing_object_name}"
                if not check_success
                else "",
            }
        except Exception as e:
            logger.error("Error during schema and database check", exc_info=True)
            return {
                "success": False,
                "successMessage": "",
                "failureMessage": "Schemas and Databases check failed",
                "error": str(e),
            }
        finally:
            if connection:
                connection.close()

    @staticmethod
    def extract_allowed_schemas(
        schemas_results: List[Dict[str, str]],
    ) -> Tuple[Set[str], Set[str]]:
        allowed_databases: Set[str] = set()
        allowed_schemas: Set[str] = set()
        for schema in schemas_results:
            allowed_databases.add(schema[Preflight.DATABASE_KEY])
            allowed_schemas.add(
                f"{schema[Preflight.DATABASE_KEY]}.{schema[Preflight.SCHEMA_KEY]}"
            )
        return allowed_databases, allowed_schemas

    @staticmethod
    def validate_filters(
        include_filter: Dict[str, List[str]],
        allowed_databases: Set[str],
        allowed_schemas: Set[str],
    ) -> Tuple[bool, str]:
        for filtered_db, filtered_schemas in include_filter.items():
            db = filtered_db.strip("^$")
            if db not in allowed_databases:
                return False, f"{db} database"
            for schema in filtered_schemas:
                sch = schema.strip("^$")
                if f"{db}.{sch}" not in allowed_schemas:
                    return False, f"{db}.{sch} schema"
        return True, ""

    @staticmethod
    def tables_check(payload: PreflightPayload) -> Dict[str, Any]:
        logger.info("Starting tables check")
        connection = None
        try:
            normalized_include_regex, normalized_exclude_regex, exclude_table = (
                Preflight.prepare_filters(
                    payload.form_data.include_filter,
                    payload.form_data.exclude_filter,
                    payload.form_data.temp_table_regex,
                )
            )

            credentials = payload.credentials.get_credential_config()
            connection = psycopg2.connect(**credentials.model_dump())
            cursor = connection.cursor()
            query = TABLES_CHECK_SQL.format(
                exclude_table=exclude_table,
                normalized_exclude_regex=normalized_exclude_regex,
                normalized_include_regex=normalized_include_regex,
            )
            cursor.execute(query)
            result = cursor.fetchone()[0]

            return {
                "success": True,
                "successMessage": f"Tables check successful. Table count: {result}",
                "failureMessage": "",
            }
        except Exception as e:
            logger.error("Error during tables check", exc_info=True)
            return {
                "success": False,
                "successMessage": "",
                "failureMessage": "Tables check failed",
                "error": str(e),
            }
        finally:
            if connection:
                connection.close()

    @staticmethod
    def prepare_filters(
        include_filter_str: str, exclude_filter_str: str, temp_table_regex_str: str
    ) -> Tuple[str, str, str]:
        include_filter = json.loads(include_filter_str)
        exclude_filter = json.loads(exclude_filter_str)

        normalized_include_filter_list = Preflight.normalize_filters(
            include_filter, True
        )
        normalized_exclude_filter_list = Preflight.normalize_filters(
            exclude_filter, False
        )

        normalized_include_regex = (
            "|".join(normalized_include_filter_list)
            if normalized_include_filter_list
            else ".*"
        )
        normalized_exclude_regex = (
            "|".join(normalized_exclude_filter_list)
            if normalized_exclude_filter_list
            else "$^"
        )

        exclude_table = temp_table_regex_str if temp_table_regex_str else "$^"

        return normalized_include_regex, normalized_exclude_regex, exclude_table

    @staticmethod
    def normalize_filters(
        filter_dict: Dict[str, List[str]], is_include: bool
    ) -> List[str]:
        normalized_filter_list: List[str] = []
        for filtered_db, filtered_schemas in filter_dict.items():
            db = filtered_db.strip("^$")
            if not filtered_schemas:
                normalized_filter_list.append(f"{db}.*")
            else:
                for schema in filtered_schemas:
                    sch = schema.lstrip(
                        "^"
                    )  # we do not strip out the $ as it is used to match the end of the string
                    normalized_filter_list.append(f"{db}.{sch}")
        return normalized_filter_list
