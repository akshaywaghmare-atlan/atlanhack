import logging
from temporalio.client import Client
from temporalio.worker import Worker
from app.workflow.workflow import ExtractionWorkflow
from app.workflow.activities import ExtractionActivities
from app.const import METADATA_EXTRACTION_TASK_QUEUE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_worker():
    client = await Client.connect("localhost:7233", namespace="default")

    worker = Worker(
        client,
        task_queue=METADATA_EXTRACTION_TASK_QUEUE,
        workflows=[ExtractionWorkflow],
        activities=[
            ExtractionActivities.create_output_directory,
            ExtractionActivities.extract_and_store_metadata,
            ExtractionActivities.push_results_to_object_store,
        ],
    )

    logger.info("Starting worker")
    await worker.run()


def start_worker():
    import asyncio

    asyncio.run(run_worker())


def stop_worker():
    pass
