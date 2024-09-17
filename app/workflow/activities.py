import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

from temporalio import activity
from app.common.converter import transform_metadata
from app.common.utils import connect_to_db
from sdk.interfaces.platform import Platform
from app.common.schema import PydanticJSONEncoder
from app.dto.workflow import ExtractionConfig
import os
from typing import Dict, List, Any


class ExtractionActivities:
    @staticmethod
    @activity.defn
    async def create_output_directory(output_prefix: str) -> None:
        os.makedirs(output_prefix, exist_ok=True)
        os.makedirs(os.path.join(output_prefix, "raw"), exist_ok=True)
        os.makedirs(os.path.join(output_prefix, "transformed"), exist_ok=True)

        activity.logger.info(f"Created output directory: {output_prefix}")

    @staticmethod
    @activity.defn
    async def extract_metadata(
        extConfig: ExtractionConfig,
    ) -> Dict[str, Dict[str, int]]:
        workflow_config = extConfig.workflowConfig
        typename = extConfig.typename
        query = extConfig.query

        activity.logger.info(f"Starting metadata extraction for {typename}")
        credentials = Platform.extract_credentials(workflow_config.credentialsGUID)
        conn = connect_to_db(credentials)

        try:
            # Execute query and fetch results
            results = await ExtractionActivities._execute_query(conn, query)

            # Process and write results
            summary = ExtractionActivities._process_and_write_results(
                results, typename, workflow_config.outputPath, typename
            )

            activity.logger.info(f"Completed metadata extraction for {typename}:")
            activity.logger.info(
                f"Raw assets extracted for {typename}: {summary['raw']}"
            )
            activity.logger.info(
                f"Assets transformed for {typename}: {summary['transformed']}"
            )
            activity.logger.info(f"Assets errored for {typename}: {summary['errored']}")

        except Exception as e:
            activity.logger.error(f"Error extracting metadata for {typename}: {e}")
            raise e
        finally:
            conn.close()

        return {typename: summary}

    @staticmethod
    async def _execute_query(conn: Any, query: str) -> List[Dict[str, Any]]:
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(
                pool, ExtractionActivities._execute_query_sync, conn, query
            )

    @staticmethod
    def _execute_query_sync(conn: Any, query: str) -> List[Dict[str, Any]]:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            column_names = [desc[0] for desc in cursor.description]
            results: List[Dict[str, Any]] = []
            while True:
                rows = cursor.fetchmany(1000)
                if not rows:
                    break
                results.extend([dict(zip(column_names, row)) for row in rows])
        except Exception as e:
            activity.logger.error(f"Error executing query: {e}")
            raise

        return results

    @staticmethod
    def _process_and_write_results(
        results: List[Dict[str, Any]], typename: str, output_path: str, file_name: str
    ) -> Dict[str, int]:
        summary = {"raw": 0, "transformed": 0, "errored": 0}
        raw_file = os.path.join(output_path, "raw", f"{file_name}.json")
        transformed_file = os.path.join(output_path, "transformed", f"{file_name}.json")

        with open(raw_file, "w") as raw_f, open(transformed_file, "w") as trans_f:
            for row in results:
                try:
                    # Store raw data
                    json.dump(row, raw_f)
                    raw_f.write("\n")
                    summary["raw"] += 1

                    # Transform and store data
                    transformed_data = transform_metadata(typename, row)
                    if transformed_data is not None:
                        json.dump(
                            transformed_data.model_dump(),
                            trans_f,
                            cls=PydanticJSONEncoder,
                        )
                        trans_f.write("\n")
                        summary["transformed"] += 1
                    else:
                        activity.logger.warning(
                            f"Skipped invalid {typename} data: {row}"
                        )
                        summary["errored"] += 1
                except Exception as row_error:
                    activity.logger.error(
                        f"Error processing row for {typename}: {row_error}"
                    )
                    summary["errored"] += 1

        return summary

    @staticmethod
    @activity.defn
    async def push_results_to_object_store(output_config: Dict[str, str]) -> None:
        activity.logger.info("Pushing results to object store")
        try:
            output_prefix, output_path = (
                output_config["output_prefix"],
                output_config["output_path"],
            )
            Platform.push_to_object_store(output_prefix, output_path)
        except Exception as e:
            activity.logger.error(f"Error pushing results to object store: {e}")
