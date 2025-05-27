import asyncio
import time
import uuid

from application_sdk.application.metadata_extraction.sql import (
    BaseSQLMetadataExtractionApplication,
)
from application_sdk.common.error_codes import ApiError
from application_sdk.constants import APPLICATION_NAME
from application_sdk.observability.logger_adaptor import get_logger
from application_sdk.observability.metrics_adaptor import MetricType, get_metrics
from application_sdk.observability.traces_adaptor import TracingContext, get_traces
from application_sdk.transformers.query import QueryBasedTransformer

from app.clients import SQLClient


async def main():
    # Initialize observability components
    logger = get_logger(__name__)
    metrics = get_metrics()
    traces = get_traces()

    # Create tracing context
    trace_id = str(uuid.uuid4())
    root_span_id = str(uuid.uuid4())
    start_time = time.time()

    tracing = TracingContext(logger, metrics, traces, trace_id, root_span_id)

    try:
        logger.info("Starting application initialization")

        # Initialize the application
        application = BaseSQLMetadataExtractionApplication(
            name=APPLICATION_NAME,
            client_class=SQLClient,
            transformer_class=QueryBasedTransformer,  # type: ignore
        )

        # Execute startup operations with tracing
        async with tracing.trace_operation("workflow_setup", "Setting up workflow"):
            await application.setup_workflow()

        async with tracing.trace_operation("worker_start", "Starting worker"):
            await application.start_worker()

        async with tracing.trace_operation(
            "server_setup", "Setting up application server"
        ):
            await application.setup_server()

        async with tracing.trace_operation(
            "server_start", "Starting application server"
        ):
            await application.start_server()

        # Record overall startup metrics
        total_duration = (time.time() - start_time) * 1000

        metrics.record_metric(
            name="application_startup_duration",
            value=total_duration,
            metric_type=MetricType.HISTOGRAM,
            labels={"application": APPLICATION_NAME},
            description="Application startup duration",
            unit="milliseconds",
        )

        # Record application startup trace
        async with tracing.trace_operation(
            operation_name="application_startup",
            description="Application startup process",
        ):
            pass

        logger.info(f"Application started successfully in {total_duration:.2f}ms")

    except Exception as e:
        total_duration = (time.time() - start_time) * 1000

        # Record startup failure metrics and traces
        metrics.record_metric(
            name="application_startup_failure",
            value=1,
            metric_type=MetricType.COUNTER,
            labels={"application": APPLICATION_NAME, "error": str(e)},
            description="Application startup failures",
            unit="count",
        )

        # Use trace_operation for error case
        async with tracing.trace_operation(
            operation_name="application_startup",
            description="Application startup process",
        ):
            raise  # Re-raise the exception to trigger error handling in trace_operation

        logger.error(
            f"Failed to start application: {str(e)}",
            extra={"error_code": ApiError.SERVER_START_ERROR.code},
        )
        raise


if __name__ == "__main__":
    asyncio.run(main())
