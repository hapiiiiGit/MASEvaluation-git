from typing import Optional, Dict, Any
from loguru import logger
from prometheus_client import Counter, Gauge, Histogram, Summary, start_http_server
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
import threading
import time

class Observability:
    """
    Observability class for structured logging, metrics, and tracing.
    Integrates loguru, prometheus_client, and opentelemetry.
    """

    def __init__(self, metrics_port: int = 8000):
        # Logging setup (loguru)
        logger.remove()
        logger.add(
            sink=lambda msg: print(msg, end=""),
            level="INFO",
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            enqueue=True,
            backtrace=True,
            diagnose=True
        )

        # Metrics setup (prometheus_client)
        self._metrics_port = metrics_port
        self._metrics_started = False
        self._metrics_lock = threading.Lock()
        self._init_metrics()

        # Tracing setup (opentelemetry)
        self._init_tracing()

    def _init_metrics(self):
        # Define Prometheus metrics
        self.metrics = {
            "etl_records_processed": Counter(
                "etl_records_processed_total",
                "Total number of records processed by ETL pipeline"
            ),
            "etl_records_failed": Counter(
                "etl_records_failed_total",
                "Total number of records failed in ETL pipeline"
            ),
            "etl_processing_latency": Histogram(
                "etl_processing_latency_seconds",
                "Latency of ETL processing in seconds"
            ),
            "etl_records_inserts": Counter(
                "etl_records_inserts_total",
                "Total number of records inserted into QuestDB"
            ),
            "etl_records_insert_failures": Counter(
                "etl_records_insert_failures_total",
                "Total number of QuestDB insert failures"
            ),
            "etl_pipeline_status": Gauge(
                "etl_pipeline_status",
                "Pipeline status: 1=running, 0=stopped, -1=error"
            ),
        }
        # Start Prometheus metrics server in a background thread
        def start_metrics_server():
            with self._metrics_lock:
                if not self._metrics_started:
                    start_http_server(self._metrics_port)
                    self._metrics_started = True
                    logger.info(f"Prometheus metrics server started on port {self._metrics_port}")

        threading.Thread(target=start_metrics_server, daemon=True).start()

    def _init_tracing(self):
        # Set up OpenTelemetry tracing
        resource = Resource(attributes={"service.name": "claude_code_etl_pipeline"})
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(__name__)

    def log(self, event: str, level: str = "INFO"):
        """
        Log an event with the specified level.
        """
        if level.upper() == "DEBUG":
            logger.debug(event)
        elif level.upper() == "INFO":
            logger.info(event)
        elif level.upper() == "WARNING":
            logger.warning(event)
        elif level.upper() == "ERROR":
            logger.error(event)
        elif level.upper() == "CRITICAL":
            logger.critical(event)
        else:
            logger.info(event)

    def record_metric(self, name: str, value: float = 1.0):
        """
        Record a metric by incrementing or observing the value.
        """
        metric = self.metrics.get(name)
        if metric is None:
            logger.warning(f"Metric '{name}' not found.")
            return
        if isinstance(metric, Counter):
            metric.inc(value)
        elif isinstance(metric, Gauge):
            metric.set(value)
        elif isinstance(metric, Histogram):
            metric.observe(value)
        elif isinstance(metric, Summary):
            metric.observe(value)
        else:
            logger.warning(f"Metric '{name}' type not supported for recording.")

    def trace(self, operation: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Start and end a trace span for the given operation.
        """
        with self.tracer.start_as_current_span(operation) as span:
            if attributes:
                for k, v in attributes.items():
                    span.set_attribute(k, v)
            # Simulate operation duration for demonstration
            time.sleep(0.001)

    def get_status(self) -> Dict[str, Any]:
        """
        Get pipeline status and metrics snapshot.
        """
        status = {
            "etl_records_processed": self.metrics["etl_records_processed"]._value.get(),
            "etl_records_failed": self.metrics["etl_records_failed"]._value.get(),
            "etl_records_inserts": self.metrics["etl_records_inserts"]._value.get(),
            "etl_records_insert_failures": self.metrics["etl_records_insert_failures"]._value.get(),
            "etl_pipeline_status": self.metrics["etl_pipeline_status"]._value.get(),
        }
        return status

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics values.
        """
        return self.get_status()

    def get_logs(self, n: int = 100) -> list:
        """
        Get the last n log messages (requires loguru file sink for full support).
        """
        # For demonstration, loguru does not provide direct log retrieval from sink.
        # In production, logs should be written to a file and read from there.
        logger.warning("get_logs() is not fully implemented. Use file sink for log retrieval.")
        return []

# Example usage:
# obs = Observability(metrics_port=8000)
# obs.log("ETL pipeline started", "INFO")
# obs.record_metric("etl_records_processed", 1)
# obs.trace("transform_record", {"conversation_id": "abc123"})