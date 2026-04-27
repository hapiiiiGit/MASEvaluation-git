from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Settings:
    # model
    model_name: str = os.getenv("MODEL_NAME", "deepseek-v3-250324")
    base_url: str | None = os.getenv("BASE_URL","https://yunwu.ai/v1")
    api_key: str | None = os.getenv("OPENAI_API_KEY","sk-83TcEkefksg6WAcy28HDfj5zilVIvmtkLN0F0hetYEluOv1I")
    temperature: float = float(os.getenv("MODEL_TEMPERATURE", "0.0"))

    # experiment
    max_iterations: int = int(os.getenv("MAX_ITERATIONS", "4"))
    programmer_mode: str = os.getenv("PROGRAMMER_MODE", "")

    # run
    graph_name: str = os.getenv("GRAPH_NAME", "programmer_reviewer")
    task_file: str = os.getenv("TASK_FILE", "Task/pro-70.txt")
    output_root: str = os.getenv("OUTPUT_ROOT", "outputs/deepseek2-runs")
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    retry_wait_seconds: float = float(os.getenv("RETRY_WAIT_SECONDS", "5"))

settings = Settings()