from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
from app.workflow.activities import ExtractionActivities
from app.models.workflow import ExtractionConfig, WorkflowConfig

@workflow.defn
class ExtractionWorkflow:
    @workflow.run
    async def extract_metadata(self, config: WorkflowConfig) -> None:
        workflow.logger.info(f"Starting extraction workflow for {config.workflowId}")
        retry_policy = RetryPolicy(maximum_attempts=3)

        workflow_run_id = workflow.info().run_id
        config.outputPath = f"{config.outputPrefix}/{config.workflowId}/{workflow_run_id}"

        # Create output directory
        await workflow.execute_activity(
            ExtractionActivities.create_output_directory,
            config.outputPath,
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(minutes=5)
        )

        # Define metadata types and their corresponding queries
        metadata_types = {
            "database": "SELECT * FROM pg_database WHERE datistemplate = false;",
            "schema": "SELECT * FROM information_schema.schemata  WHERE schema_name NOT LIKE 'pg_%' AND schema_name != 'information_schema'",
            "table": config.tableCompanionSQL,
            "column": config.columnCompanionSQL
        }

        # TODO: run all of the following activities in parallel
        # Extract and store metadata for each type
        for typename, query in metadata_types.items():
            await workflow.execute_activity(
                ExtractionActivities.extract_and_store_metadata,
                ExtractionConfig(
                    workflowConfig=config,
                    typename=typename,
                    query=query
                ),
                retry_policy=retry_policy,
                start_to_close_timeout=timedelta(minutes=30)
            )

        # Push results to object store
        await workflow.execute_activity(
            ExtractionActivities.push_results_to_object_store,
            {
                "output_prefix": config.outputPrefix,
                "output_path": config.outputPath
            },
            retry_policy=retry_policy,
            start_to_close_timeout=timedelta(minutes=10)
        )

        # TODO: cleanup output directory

        workflow.logger.info(f"Extraction workflow completed for {config.workflowId}")