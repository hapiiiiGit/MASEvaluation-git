import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "review-pylint"/"qwen"
JUDGE_FILES = {
    "gpt": INPUT_DIR / "gpt.json",
    "claude": INPUT_DIR / "claude.json",
    "gemini": INPUT_DIR / "gemini.json",
}
OUTPUT_FILE = INPUT_DIR / "featureRate.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def task_sort_key(task_id: str) -> tuple[int, str]:
    try:
        return (0, int(task_id.replace("task_", "")))
    except ValueError:
        return (1, task_id)


def calc_fr_majority(judge_data: dict, task_id: str) -> dict | None:
    finished_by_model: dict[str, set[int]] = {}
    feature_total = 0
    task_text = ""
    features = []
    source_models = []

    for model_name, model_data in judge_data.items():
        task_data = model_data.get(task_id)
        if not task_data:
            continue

        feature_total = max(feature_total, int(task_data.get("feature_total", 0)))
        finished_by_model[model_name] = {
            int(index) for index in task_data.get("feature_finish", [])
        }
        task_text = task_text or task_data.get("task", "")
        features = features or task_data.get("features", [])
        judge_model = task_data.get("judge_model")
        source_models.append(judge_model or model_name)

    if not finished_by_model or feature_total == 0:
        return None

    majority_finish = []
    for index in range(1, feature_total + 1):
        votes = sum(1 for finished in finished_by_model.values() if index in finished)
        if votes >= 2:
            majority_finish.append(index)

    feature_results = {
        str(index): index in majority_finish
        for index in range(1, feature_total + 1)
    }

    return {
        "task_id": task_id,
        "task": task_text,
        "feature_total": feature_total,
        "feature_finish": majority_finish,
        "feature_results": feature_results,
        "completion_rate": round(len(majority_finish) / feature_total, 4),
        "features": features,
        "vote_models": source_models,
    }


def main() -> None:
    judge_data = {
        name: load_json(path)
        for name, path in JUDGE_FILES.items()
        if path.exists()
    }

    if not judge_data:
        raise FileNotFoundError(f"No judge files found under: {INPUT_DIR}")

    all_task_ids = sorted(
        {task_id for model_data in judge_data.values() for task_id in model_data},
        key=task_sort_key,
    )

    results = {}
    for task_id in all_task_ids:
        result = calc_fr_majority(judge_data, task_id)
        if result is None:
            print(f"{task_id} | missing valid feature data")
            continue

        results[task_id] = result
        print(
            f"{task_id} | "
            f"completion_rate: {result['completion_rate']:.2%} | "
            f"finish: {len(result['feature_finish'])}/{result['feature_total']} | "
            f"feature_finish: {result['feature_finish']}"
        )

    OUTPUT_FILE.write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nSaved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
