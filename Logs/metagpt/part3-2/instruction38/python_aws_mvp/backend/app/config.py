import os
from functools import lru_cache
from pydantic import BaseSettings, Field
from typing import List, Optional
from datetime import datetime, timedelta

class Settings(BaseSettings):
    # App settings
    HOST: str = Field(default="0.0.0.0", env="APP_HOST")
    PORT: int = Field(default=8000, env="APP_PORT")
    RELOAD: bool = Field(default=True, env="APP_RELOAD")
    ENVIRONMENT: str = Field(default="dev", env="ENVIRONMENT")
    ALLOWED_ORIGINS: List[str] = Field(default=["*"], env="ALLOWED_ORIGINS")

    # JWT settings
    JWT_SECRET_KEY: str = Field(default="supersecretkey", env="JWT_SECRET_KEY")

    # AWS settings
    AWS_ACCESS_KEY_ID: str = Field(default="", env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    AWS_S3_BUCKET: str = Field(default="", env="AWS_S3_BUCKET")

    # CloudWatch settings
    CLOUDWATCH_LOG_GROUP: str = Field(default="python_aws_mvp_logs", env="CLOUDWATCH_LOG_GROUP")
    CLOUDWATCH_LOG_STREAM: str = Field(default="main", env="CLOUDWATCH_LOG_STREAM")
    CLOUDWATCH_NAMESPACE: str = Field(default="python_aws_mvp", env="CLOUDWATCH_NAMESPACE")
    CLOUDWATCH_METRIC_NAME: str = Field(default="RequestCount", env="CLOUDWATCH_METRIC_NAME")
    METRIC_START_TIME: datetime = Field(default_factory=lambda: datetime.utcnow() - timedelta(hours=1))
    METRIC_END_TIME: datetime = Field(default_factory=lambda: datetime.utcnow())

    # Stripe settings
    STRIPE_API_KEY: str = Field(default="", env="STRIPE_API_KEY")

    # Sentry settings
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()