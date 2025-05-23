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
from application_sdk.observability.traces_adaptor import get_traces
from application_sdk.transformers.query import QueryBasedTransformer

from app.clients import SQLClient


async def main():
    # Initialize logger, metrics and traces
    logger = get_logger(__name__)
    metrics = get_metrics()
    traces = get_traces()

    # Create root trace for application startup
    trace_id = str(uuid.uuid4())
    root_span_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        logger.info("Starting application initialization")

        # Initialize the application
        application = BaseSQLMetadataExtractionApplication(
            name=APPLICATION_NAME,
            client_class=SQLClient,
            transformer_class=QueryBasedTransformer,  # type: ignore
        )

        # Setup the workflow
        logger.info("Setting up workflow")
        workflow_span_id = str(uuid.uuid4())
        workflow_start_time = time.time()
        await application.setup_workflow()
        workflow_duration = (time.time() - workflow_start_time) * 1000
        traces.record_trace(
            name="workflow_setup",
            trace_id=trace_id,
            span_id=workflow_span_id,
            kind="INTERNAL",
            status_code="OK",
            parent_span_id=root_span_id,
            attributes={"application": APPLICATION_NAME, "operation": "workflow_setup"},
            events=[{"name": "workflow_setup_success", "timestamp": time.time()}],
            duration_ms=workflow_duration,
        )
        metrics.record_metric(
            name="workflow_setup_success",
            value=1,
            metric_type=MetricType.COUNTER,
            labels={"application": APPLICATION_NAME},
            description="Successful workflow setup",
            unit="count",
        )

        # Start the worker
        logger.info("Starting worker")
        worker_span_id = str(uuid.uuid4())
        worker_start_time = time.time()
        await application.start_worker()
        worker_duration = (time.time() - worker_start_time) * 1000
        traces.record_trace(
            name="worker_start",
            trace_id=trace_id,
            span_id=worker_span_id,
            kind="INTERNAL",
            status_code="OK",
            parent_span_id=root_span_id,
            attributes={"application": APPLICATION_NAME, "operation": "worker_start"},
            events=[{"name": "worker_start_success", "timestamp": time.time()}],
            duration_ms=worker_duration,
        )
        metrics.record_metric(
            name="worker_start_success",
            value=1,
            metric_type=MetricType.COUNTER,
            labels={"application": APPLICATION_NAME},
            description="Successful worker start",
            unit="count",
        )

        # Setup the application server
        logger.info("Setting up application server")
        server_setup_span_id = str(uuid.uuid4())
        server_setup_start_time = time.time()
        await application.setup_server()
        server_setup_duration = (time.time() - server_setup_start_time) * 1000
        traces.record_trace(
            name="server_setup",
            trace_id=trace_id,
            span_id=server_setup_span_id,
            kind="INTERNAL",
            status_code="OK",
            parent_span_id=root_span_id,
            attributes={"application": APPLICATION_NAME, "operation": "server_setup"},
            events=[{"name": "server_setup_success", "timestamp": time.time()}],
            duration_ms=server_setup_duration,
        )
        metrics.record_metric(
            name="server_setup_success",
            value=1,
            metric_type=MetricType.COUNTER,
            labels={"application": APPLICATION_NAME},
            description="Successful server setup",
            unit="count",
        )

        # Start the application server
        logger.info("Starting application server")
        server_start_span_id = str(uuid.uuid4())
        server_start_time = time.time()
        await application.start_server()
        server_start_duration = (time.time() - server_start_time) * 1000
        traces.record_trace(
            name="server_start",
            trace_id=trace_id,
            span_id=server_start_span_id,
            kind="INTERNAL",
            status_code="OK",
            parent_span_id=root_span_id,
            attributes={"application": APPLICATION_NAME, "operation": "server_start"},
            events=[{"name": "server_start_success", "timestamp": time.time()}],
            duration_ms=server_start_duration,
        )

        # Record application startup duration
        duration = (time.time() - start_time) * 1000  # Convert to milliseconds
        metrics.record_metric(
            name="application_startup_duration",
            value=duration,
            metric_type=MetricType.HISTOGRAM,
            labels={"application": APPLICATION_NAME},
            description="Application startup duration",
            unit="milliseconds",
        )

        # Record root trace
        traces.record_trace(
            name="application_startup",
            trace_id=trace_id,
            span_id=root_span_id,
            kind="INTERNAL",
            status_code="OK",
            attributes={"application": APPLICATION_NAME},
            events=[
                {
                    "name": "application_startup_success",
                    "timestamp": time.time(),
                    "attributes": {"duration_ms": duration},
                }
            ],
            duration_ms=duration,
        )

        logger.info(f"Application started successfully in {duration:.2f}ms")

    except Exception as e:
        # Record application startup failure
        metrics.record_metric(
            name="application_startup_failure",
            value=1,
            metric_type=MetricType.COUNTER,
            labels={"application": APPLICATION_NAME, "error": str(e)},
            description="Application startup failures",
            unit="count",
        )

        # Record failure trace
        traces.record_trace(
            name="application_startup",
            trace_id=trace_id,
            span_id=root_span_id,
            kind="INTERNAL",
            status_code="ERROR",
            attributes={"application": APPLICATION_NAME},
            events=[
                {
                    "name": "application_startup_failure",
                    "timestamp": time.time(),
                    "attributes": {"error": str(e)},
                }
            ],
            duration_ms=(time.time() - start_time) * 1000,
        )

        logger.error(
            f"Failed to start application: {str(e)}",
            extra={"error_code": ApiError.SERVER_START_ERROR.code},
        )
        raise


if __name__ == "__main__":
    asyncio.run(main())
