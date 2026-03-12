import logging
import boto3
import sentry_sdk
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
from .config import get_settings

settings = get_settings()

# Initialize logging
logger = logging.getLogger("python_aws_mvp")
logger.setLevel(logging.INFO)

# Initialize Sentry
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
        environment=settings.ENVIRONMENT,
    )

# Initialize CloudWatch client
cloudwatch_client = boto3.client(
    "cloudwatch",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION,
)

class LogEventRequest(BaseModel):
    event: Dict[str, Any]

class TrackErrorRequest(BaseModel):
    error_message: str
    error_type: str
    details: Dict[str, Any] = {}

class MetricsResponse(BaseModel):
    metrics: Dict[str, Any]

class ObservabilityManager:
    @staticmethod
    def log_event(event: Dict[str, Any]) -> None:
        # Log locally
        logger.info(f"Event: {event}")

        # Send to CloudWatch
        try:
            cloudwatch_client.put_log_events(
                logGroupName=settings.CLOUDWATCH_LOG_GROUP,
                logStreamName=settings.CLOUDWATCH_LOG_STREAM,
                logEvents=[
                    {
                        'timestamp': int(event.get("timestamp", 0)),
                        'message': str(event)
                    }
                ]
            )
        except Exception as e:
            logger.error(f"Failed to send log to CloudWatch: {e}")

    @staticmethod
    def track_error(error: Exception) -> None:
        # Log locally
        logger.error(f"Error: {str(error)}")
        # Send to Sentry
        sentry_sdk.capture_exception(error)

    @staticmethod
    def get_metrics() -> Dict[str, Any]:
        # Example: Get custom metrics from CloudWatch
        try:
            response = cloudwatch_client.get_metric_statistics(
                Namespace=settings.CLOUDWATCH_NAMESPACE,
                MetricName=settings.CLOUDWATCH_METRIC_NAME,
                Dimensions=[
                    {
                        'Name': 'Service',
                        'Value': 'python_aws_mvp'
                    },
                ],
                StartTime=settings.METRIC_START_TIME,
                EndTime=settings.METRIC_END_TIME,
                Period=300,
                Statistics=['Sum', 'Average']
            )
            return {"metrics": response.get("Datapoints", [])}
        except Exception as e:
            logger.error(f"Failed to get metrics from CloudWatch: {e}")
            return {"metrics": []}

# FastAPI router for observability
observability_router = APIRouter()

@observability_router.post("/log-event", summary="Log an event to CloudWatch")
async def log_event(request: LogEventRequest):
    ObservabilityManager.log_event(request.event)
    return {"status": "event logged"}

@observability_router.post("/track-error", summary="Track an error in Sentry")
async def track_error(request: TrackErrorRequest):
    try:
        error = Exception(f"{request.error_type}: {request.error_message} | Details: {request.details}")
        ObservabilityManager.track_error(error)
        return {"status": "error tracked"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track error: {str(e)}"
        )

@observability_router.get("/metrics", response_model=MetricsResponse, summary="Get service metrics from CloudWatch")
async def get_metrics():
    metrics = ObservabilityManager.get_metrics()
    return MetricsResponse(**metrics)

def get_observability_router():
    return observability_router