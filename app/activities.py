import asyncio
import json
import os
import shutil
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

import aiofiles
import psycopg2
from phoenix_sdk.common.converter import transform_metadata
from phoenix_sdk.common.schema import PydanticJSONEncoder
from phoenix_sdk.dto.workflow import ExtractionConfig
from phoenix_sdk.interfaces.platform import Platform
from phoenix_sdk.workflows.utils.activity import auto_heartbeater
from temporalio import activity

from app.const import CONNECTOR_NAME, CONNECTOR_TYPE


class ExtractionActivities:
    @staticmethod
    @activity.defn
    async def setup_output_directory(output_prefix: str) -> None:
        os.makedirs(output_prefix, exist_ok=True)
        os.makedirs(os.path.join(output_prefix, "raw"), exist_ok=True)
        os.makedirs(os.path.join(output_prefix, "transformed"), exist_ok=True)

        activity.logger.info(f"Created output directory: {output_prefix}")

    @staticmethod
    @activity.defn
    @auto_heartbeater
    async def extract_metadata(
        extConfig: ExtractionConfig,
    ) -> Dict[str, Dict[str, int]]:
        workflow_config = extConfig.workflowConfig
        typename = extConfig.typename
        query = extConfig.query

        activity.logger.info(f"Starting metadata extraction for {typename}")
        credentials = Platform.extract_credentials(workflow_config.credentialsGUID)
        connection = None

        try:
            connection = psycopg2.connect(**credentials.model_dump())
            summary = await ExtractionActivities._execute_query_and_process(
                connection, query, typename, workflow_config.outputPath
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
            if connection:
                connection.close()

        return {typename: summary}

    @staticmethod
    async def _execute_query_and_process(
        connection: Any,
        query: str,
        typename: str,
        output_path: str,
        batch_size: int = 100000,
    ) -> Dict[str, int]:
        activity.logger.info(f"Executing query for {typename}")
        summary = {"raw": 0, "transformed": 0, "errored": 0}

        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            # Use a unique name for the server-side cursor
            cursor_name = f"cursor_{typename}_{uuid.uuid4()}"
            cursor = await loop.run_in_executor(
                pool, lambda: connection.cursor(name=cursor_name)
            )

            try:
                # Execute the query
                await loop.run_in_executor(pool, cursor.execute, query)
                column_names: List[str] = []
                total_rows, chunk_number = 0, 0

                while True:
                    # Fetch a batch of results
                    start_time = time.time()
                    rows = await loop.run_in_executor(
                        pool, cursor.fetchmany, batch_size
                    )
                    if not column_names:
                        column_names = [desc[0] for desc in cursor.description]

                    if not rows:
                        break

                    results = [dict(zip(column_names, row)) for row in rows]
                    total_rows += len(rows)

                    end_time = time.time()
                    activity.logger.info(
                        f"Fetched {len(rows)} rows in {end_time - start_time} seconds. Total rows: {total_rows}"
                    )

                    await ExtractionActivities._process_batch(
                        results, typename, output_path, summary, chunk_number
                    )

                    chunk_number += 1

                chunk_meta_file = os.path.join(output_path, f"{typename}-chunks.txt")
                async with aiofiles.open(chunk_meta_file, "w") as chunk_meta_f:
                    await chunk_meta_f.write(str(chunk_number))
            except Exception as e:
                activity.logger.error(f"Error executing query for {typename}: {e}")
                raise e
            finally:
                await loop.run_in_executor(pool, cursor.close)

        activity.logger.info(f"Completed processing results for {typename}")
        return summary

    @staticmethod
    async def _process_batch(
        results: List[Dict[str, Any]],
        typename: str,
        output_path: str,
        summary: Dict[str, int],
        chunk_number: int,
    ) -> None:
        raw_batch: List[str] = []
        transformed_batch: List[str] = []

        for row in results:
            try:
                raw_batch.append(json.dumps(row))
                summary["raw"] += 1

                transformed_data = transform_metadata(
                    CONNECTOR_NAME, CONNECTOR_TYPE, typename, row
                )
                if transformed_data is not None:
                    transformed_batch.append(
                        json.dumps(
                            transformed_data.model_dump(), cls=PydanticJSONEncoder
                        )
                    )
                    summary["transformed"] += 1
                else:
                    activity.logger.warning(f"Skipped invalid {typename} data: {row}")
                    summary["errored"] += 1
            except Exception as row_error:
                activity.logger.error(
                    f"Error processing row for {typename}: {row_error}"
                )
                summary["errored"] += 1

        # Write batches to files
        raw_file = os.path.join(output_path, "raw", f"{typename}-{chunk_number}.json")
        transformed_file = os.path.join(
            output_path, "transformed", f"{typename}-{chunk_number}.json"
        )

        async with aiofiles.open(raw_file, "a") as raw_f:
            await raw_f.write("\n".join(raw_batch) + "\n")

        async with aiofiles.open(transformed_file, "a") as trans_f:
            await trans_f.write("\n".join(transformed_batch) + "\n")

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
            raise e

    @staticmethod
    @activity.defn
    async def teardown_output_directory(output_prefix: str) -> None:
        activity.logger.info(f"Tearing down output directory: {output_prefix}")
        shutil.rmtree(output_prefix)
