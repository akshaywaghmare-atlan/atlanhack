import json
from temporalio import activity
from app.common.converter import transform_metadata
from app.common.utils import connect_to_db
from sdk.interfaces.platform import Platform
from app.common.schema import PydanticJSONEncoder
from app.dto.workflow import ExtractionConfig
import os
from typing import Dict


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
    async def extract_and_store_metadata(
        extConfig: ExtractionConfig,
    ) -> Dict[str, Dict[str, int]]:
        workflow_config = extConfig.workflowConfig
        typename = extConfig.typename
        query = extConfig.query

        activity.logger.info(f"Starting metadata extraction for {typename}")
        credentials = Platform.extract_credentials(workflow_config.credentialsGUID)
        conn = connect_to_db(credentials)

        summary = {"raw": 0, "transformed": 0, "errored": 0}

        try:
            cursor = conn.cursor()
            cursor.execute(query)

            raw_file = os.path.join(
                workflow_config.outputPath, "raw", f"{typename}.json"
            )
            transformed_file = os.path.join(
                workflow_config.outputPath, "transformed", f"{typename}.json"
            )

            with open(raw_file, "w") as raw_f, open(transformed_file, "w") as trans_f:
                while True:
                    cursor_rows = cursor.fetchmany(1000)  # Fetch 1000 rows at a time
                    if not cursor_rows:
                        break

                    column_names = [desc[0] for desc in cursor.description]
                    rows = [dict(zip(column_names, row)) for row in cursor_rows]

                    for row in rows:
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
    @activity.defn
    async def push_results_to_object_store(output_config: dict) -> None:
        activity.logger.info("Pushing results to object store")
        try:
            output_prefix, output_path = (
                output_config["output_prefix"],
                output_config["output_path"],
            )
            Platform.push_to_object_store(output_prefix, output_path)
        except Exception as e:
            activity.logger.error(f"Error pushing results to object store: {e}")
