import json
from typing import Dict
from temporalio import activity
from app.common.converter import transform_metadata
from app.common.utils import connect_to_db
from sdk.interfaces.platform import Platform
from app.common.schema import PydanticJSONEncoder
from app.dto.workflow import ExtractionConfig
import os


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
    async def extract_and_store_metadata(extConfig: ExtractionConfig) -> None:
        config = extConfig.workflowConfig
        typename = extConfig.typename
        query = extConfig.query

        activity.logger.info(f"Extracting metadata for {typename}")
        credentials = Platform.extract_credentials(config.credentialsGUID)
        conn = connect_to_db(credentials)

        try:
            cursor = conn.cursor()
            cursor.execute(query)

            raw_file = os.path.join(config.outputPath, "raw", f"{typename}.json")
            transformed_file = os.path.join(
                config.outputPath, "transformed", f"{typename}.json"
            )

            with open(raw_file, "w") as raw_f, open(transformed_file, "w") as trans_f:
                while True:
                    cursor_rows = cursor.fetchmany(1000)  # Fetch 1000 rows at a time
                    column_names = [desc[0] for desc in cursor.description]
                    rows = [dict(zip(column_names, row)) for row in cursor_rows]

                    if not rows:
                        break
                    for row in rows:
                        # Store raw data
                        json.dump(row, raw_f)
                        raw_f.write("\n")

                        # Transform and store data
                        transformed_data = transform_metadata(typename, row)
                        if transformed_data is not None:
                            json.dump(
                                transformed_data.model_dump(),
                                trans_f,
                                cls=PydanticJSONEncoder,
                            )
                            trans_f.write("\n")
                        else:
                            activity.logger.warning(
                                f"Skipped invalid {typename} data: {row}"
                            )

        except Exception as e:
            activity.logger.error(f"Error extracting metadata for {typename}: {e}")
        finally:
            conn.close()

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
