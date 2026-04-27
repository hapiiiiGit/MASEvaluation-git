from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from multiAgent.config.setting import settings
from multiAgent.graphs import GRAPH_REGISTRY


GRAPH_NAME = "plan_programmer_tester"
DEFAULT_BASE_URL = "https://yunwu.ai/v1"


@dataclass(frozen=True)
class ModelConfig:
    folder_name: str
    model_name: str
    api_key: str
    base_url: str = DEFAULT_BASE_URL


MODEL_CONFIGS: list[ModelConfig] = [
    ModelConfig(
        folder_name="claude-haiku-4-5-20251001-runs",
        model_name="claude-haiku-4-5-20251001",
        api_key="sk-BqpzZp4wn8frQlcPgyTaXgf8MQoDbm6pYLpioKvqVi8blyaa",
    ),
    ModelConfig(
        folder_name="deepseek-v3-250324-runs",
        model_name="deepseek-v3-250324",
        api_key="sk-83TcEkefksg6WAcy28HDfj5zilVIvmtkLN0F0hetYEluOv1I",
    ),
    ModelConfig(
        folder_name="gemini-2.5-pro-runs",
        model_name="gemini-2.5-pro",
        api_key="sk-xO8o6Bhi3LTz3dwTZ3zT3IRpH51HOFVRt5eJ4J6POWgfveyn",
    ),
    ModelConfig(
        folder_name="gpt-4.1-2025-04-14-runs",
        model_name="gpt-4.1-2025-04-14",
        api_key="sk-z0mMzozNeGFjwoULIrG7kKZ9UiXdvO9PRWK1oI5DILpbnJ8R",
    ),
    ModelConfig(
        folder_name="qwen2.5-coder-32b-instruct-runs",
        model_name="qwen2.5-coder-32b-instruct",
        api_key="sk-83TcEkefksg6WAcy28HDfj5zilVIvmtkLN0F0hetYEluOv1I",
    ),
]


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def resolve_task_file(path_str: str) -> Path:
    candidates = [
        repo_root() / path_str,
        Path(__file__).resolve().parent / path_str,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Task file not found: {path_str}")


def load_task_file(path_str: str) -> list[str]:
    path = resolve_task_file(path_str)
    tasks: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if text:
            tasks.append(text)
    return tasks


def load_all_tasks() -> tuple[list[dict[str, Any]], list[str]]:
    source_files = ["Task/pro-50.txt", "Task/pro-70.txt"]
    combined: list[dict[str, Any]] = []

    task_index = 1
    for source_file in source_files:
        for source_line_no, task in enumerate(load_task_file(source_file), start=1):
            combined.append(
                {
                    "task_id": f"task_{task_index:04d}",
                    "task": task,
                    "source_file": source_file,
                    "source_line_no": source_line_no,
                }
            )
            task_index += 1

    return combined, source_files


def load_manifest(manifest_path: Path) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}

    if not manifest_path.exists():
        return records

    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        records[record["task_id"]] = record

    return records


def append_manifest(manifest_path: Path, record: dict[str, Any]) -> None:
    with manifest_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def summarize_metrics(metrics: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, dict[str, Any]] = {}

    for metric in metrics:
        agent = metric.get("agent", "unknown")
        if agent not in summary:
            summary[agent] = {
                "calls": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "wall_time_s": 0.0,
            }

        summary[agent]["calls"] += 1
        summary[agent]["input_tokens"] += int(metric.get("input_tokens", 0))
        summary[agent]["output_tokens"] += int(metric.get("output_tokens", 0))
        summary[agent]["total_tokens"] += int(metric.get("total_tokens", 0))
        summary[agent]["wall_time_s"] += float(metric.get("wall_time_s", 0.0))

    return summary


def make_initial_state(task_id: str, task: str) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "task": task,
        "plans": [],
        "codes": [],
        "reviews": [],
        "test_cases": [],
        "iteration": 0,
        "max_iterations": settings.max_iterations,
        "need_revision": False,
        "programmer_mode": "",
    }


def build_plan_programmer_tester_graph(model_name: str, temperature: float):
    builder = GRAPH_REGISTRY[GRAPH_NAME]
    return builder(
        model_name=model_name,
        temperature=temperature,
    )


def configure_runtime(model: ModelConfig, output_root: Path) -> None:
    settings.graph_name = GRAPH_NAME
    settings.model_name = model.model_name
    settings.api_key = model.api_key
    settings.base_url = model.base_url
    settings.task_file = "Task/pro-50.txt + Task/pro-70.txt"
    settings.output_root = str(output_root)


def run_for_model(model: ModelConfig, tasks: list[dict[str, Any]], source_files: list[str]) -> None:
    output_root = repo_root() / "multiAgent" / "outputs" / model.folder_name
    run_dir = output_root / GRAPH_NAME
    results_dir = run_dir / "results"
    manifest_path = run_dir / "manifest.jsonl"
    summary_path = run_dir / "summary.json"

    configure_runtime(model, output_root)
    graph = build_plan_programmer_tester_graph(
        model_name=model.model_name,
        temperature=settings.temperature,
    )

    run_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    manifest = load_manifest(manifest_path)

    success_count = 0
    failed_count = 0
    skipped_count = 0

    print(f"\n===== MODEL: {model.model_name} =====")
    print(f"Output dir: {run_dir}")

    for task_item in tasks:
        task_id = task_item["task_id"]
        task = task_item["task"]
        source_file = task_item["source_file"]
        source_line_no = task_item["source_line_no"]
        result_path = results_dir / f"{task_id}.json"

        last_record = manifest.get(task_id)
        if (
            last_record is not None
            and last_record.get("status") == "SUCCESS"
            and result_path.exists()
        ):
            skipped_count += 1
            print(f"[SKIP] {model.model_name} {task_id} already finished.")
            continue

        print(f"[RUN ] {model.model_name} {task_id}")

        success = False
        last_error = ""

        for attempt in range(1, settings.max_retries + 1):
            started_at = datetime.now().isoformat(timespec="seconds")

            try:
                init_state = make_initial_state(task_id, task)
                result = graph.invoke(init_state)

                if not result.get("success", True):
                    raise RuntimeError(result.get("error", "Unknown graph failure"))

                payload = {
                    "task_id": task_id,
                    "graph_name": GRAPH_NAME,
                    "model_name": model.model_name,
                    "task": task,
                    "source_file": source_file,
                    "source_line_no": source_line_no,
                    "result": result,
                    "metrics_summary": summarize_metrics(result.get("metrics", [])),
                    "saved_at": datetime.now().isoformat(timespec="seconds"),
                }
                save_json(result_path, payload)

                record = {
                    "task_id": task_id,
                    "status": "SUCCESS",
                    "attempt": attempt,
                    "model_name": model.model_name,
                    "source_file": source_file,
                    "source_line_no": source_line_no,
                    "result_path": str(result_path),
                    "started_at": started_at,
                    "finished_at": datetime.now().isoformat(timespec="seconds"),
                }
                append_manifest(manifest_path, record)
                manifest[task_id] = record

                success = True
                success_count += 1
                print(f"[ OK ] {model.model_name} {task_id}")
                break

            except Exception as exc:
                last_error = str(exc)

                record = {
                    "task_id": task_id,
                    "status": "FAILED",
                    "attempt": attempt,
                    "model_name": model.model_name,
                    "source_file": source_file,
                    "source_line_no": source_line_no,
                    "error": last_error,
                    "started_at": started_at,
                    "finished_at": datetime.now().isoformat(timespec="seconds"),
                }
                append_manifest(manifest_path, record)
                manifest[task_id] = record

                print(
                    f"[ERR ] {model.model_name} {task_id} "
                    f"attempt={attempt} error={last_error}"
                )

                if attempt < settings.max_retries:
                    time.sleep(settings.retry_wait_seconds)

        if not success:
            failed_count += 1

    summary = {
        "graph_name": GRAPH_NAME,
        "model_name": model.model_name,
        "task_files": source_files,
        "total_tasks": len(tasks),
        "success_count": success_count,
        "failed_count": failed_count,
        "skipped_count": skipped_count,
        "finished_at": datetime.now().isoformat(timespec="seconds"),
    }
    save_json(summary_path, summary)

    print("\n===== SUMMARY =====")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def main() -> None:
    tasks, source_files = load_all_tasks()

    if not tasks:
        raise ValueError("No tasks were loaded from Task/pro-50.txt and Task/pro-70.txt.")

    print(f"Loaded {len(tasks)} tasks from {', '.join(source_files)}")

    for model in MODEL_CONFIGS:
        run_for_model(model, tasks, source_files)


if __name__ == "__main__":
    main()
