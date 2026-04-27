import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# judge prompt import
from judge_prompt import JUDGE_PROMPT


TASK_ID_PATTERN = re.compile(r"^task_(\d{4})$")

# feature path
FEATURE_JSON = Path("../Task/feature.json")
# LLM outputs path
DIR_PATH = Path("")
# report path
OUTPUT_PATH: Optional[Path] = Path("")

MODEL = os.environ.get("JUDGE_MODEL", "")
API_KEY = os.environ.get('OPENAI_API_KEY', "")
BASE_URL = os.environ.get("BASE_URL", '')
TEMPERATURE = 0.0
MAX_RETRIES = 3
SLEEP_SECONDS = 1.0
RESUME = True


TASK_IDS: Optional[List[str]] = None


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def canonical_task_id(key: str) -> Optional[str]:
    task_match = TASK_ID_PATTERN.match(key)
    if task_match:
        return key

    return None


def load_merged_tasks(merged_path: Path) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, str]]:
    raw = load_json(merged_path)
    if not isinstance(raw, dict):
        raise ValueError("feature_json must be a JSON object")

    tasks_by_id: Dict[str, Dict[str, Any]] = {}
    task_text_to_id: Dict[str, str] = {}

    for key, value in raw.items():
        if not isinstance(value, dict):
            continue
        task = value.get("task")
        features = value.get("features")
        if not isinstance(task, str) or not isinstance(features, list):
            continue

        task_id = canonical_task_id(key)
        if task_id is None:
            continue

        tasks_by_id[task_id] = {
            "source_key": key,
            "task": task,
            "features": [str(feature) for feature in features],
        }
        task_text_to_id[normalize_text(task)] = task_id

    return tasks_by_id, task_text_to_id


def extract_final_code(result_json: Dict[str, Any]) -> str:
    if isinstance(result_json.get("final_code"), str):
        return result_json["final_code"]

    nested = result_json.get("result")
    if isinstance(nested, dict) and isinstance(nested.get("final_code"), str):
        return nested["final_code"]

    raise ValueError("final_code not found")


def extract_task_text(result_json: Dict[str, Any]) -> str:
    task = result_json.get("task")
    if isinstance(task, str):
        return task

    nested = result_json.get("result")
    if isinstance(nested, dict) and isinstance(nested.get("task"), str):
        return nested["task"]

    raise ValueError("task not found")


def format_features(features: List[str]) -> str:
    return "\n".join(f"{idx}. {feature}" for idx, feature in enumerate(features, start=1))


def build_prompt(task: str, code: str, features: List[str]) -> str:
    return JUDGE_PROMPT.format(
        task=task,
        code=code,
        features=format_features(features),
    )


def extract_json_object(text: str) -> Dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("Model response does not contain a JSON object")

    return json.loads(text[start : end + 1])


def request_llm(
    *,
    prompt: str,
    model: str,
    api_key: str,
    base_url: str,
    temperature: float,
) -> Dict[str, Any]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "response_format": {"type": "json_object"},
    }

    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=300) as response:
        body = json.loads(response.read().decode("utf-8"))

    choices = body.get("choices") or []
    if not choices:
        raise ValueError("LLM response missing choices")

    message = choices[0].get("message") or {}
    content = message.get("content")

    if isinstance(content, str):
        return extract_json_object(content)

    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        return extract_json_object("".join(text_parts))

    raise ValueError("Unsupported LLM response content format")


def parse_judge_results(raw_result: Dict[str, Any], feature_count: int) -> Dict[str, bool]:
    results = raw_result.get("results")
    if not isinstance(results, dict):
        raise ValueError("Judge response JSON must contain a 'results' object")

    parsed: Dict[str, bool] = {}
    for index in range(1, feature_count + 1):
        key = str(index)
        value = results.get(key)
        if not isinstance(value, bool):
            raise ValueError(f"Feature {key} is missing or not a boolean")
        parsed[key] = value
    return parsed


def model_slug(model: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", model.strip())
    return slug or "model"


def find_merged_entry(
    result_json: Dict[str, Any],
    tasks_by_id: Dict[str, Dict[str, Any]],
    task_text_to_id: Dict[str, str],
    fallback_task_id: str,
) -> Tuple[str, Dict[str, Any]]:
    if fallback_task_id in tasks_by_id:
        return fallback_task_id, tasks_by_id[fallback_task_id]

    task_text = normalize_text(extract_task_text(result_json))
    matched_task_id = task_text_to_id.get(task_text)
    if matched_task_id:
        return matched_task_id, tasks_by_id[matched_task_id]

    raise KeyError(f"No merged task match found for {fallback_task_id}")


def collect_result_files(result_dir: Path, task_ids: Optional[List[str]]) -> List[Path]:
    files = sorted(result_dir.glob("task_*.json"))
    if not task_ids:
        return files

    wanted = set(task_ids)
    return [path for path in files if path.stem in wanted]


def judge_one(
    *,
    result_path: Path,
    tasks_by_id: Dict[str, Dict[str, Any]],
    task_text_to_id: Dict[str, str],
    model: str,
    api_key: str,
    base_url: str,
    temperature: float,
    max_retries: int,
) -> Dict[str, Any]:
    result_json = load_json(result_path)
    fallback_task_id = result_path.stem
    matched_task_id, merged_entry = find_merged_entry(
        result_json, tasks_by_id, task_text_to_id, fallback_task_id
    )

    final_code = extract_final_code(result_json)
    task_text = merged_entry["task"]
    features = merged_entry["features"]
    prompt = build_prompt(task_text, final_code, features)

    last_error: Optional[str] = None
    for attempt in range(1, max_retries + 1):
        try:
            raw_response = request_llm(
                prompt=prompt,
                model=model,
                api_key=api_key,
                base_url=base_url,
                temperature=temperature,
            )
            parsed_results = parse_judge_results(raw_response, len(features))
            feature_finish = [
                index
                for index, key in enumerate(parsed_results.keys(), start=1)
                if parsed_results[key]
            ]

            return {
                "task_id": matched_task_id,
                "result_file": result_path.name,
                "merged_key": merged_entry["source_key"],
                "task": task_text,
                "feature_total": len(features),
                "feature_finish": feature_finish,
                "feature_results": parsed_results,
                "completion_rate": round(len(feature_finish) / len(features), 4)
                if features
                else 0.0,
                "features": features,
                "judge_model": model,
            }
        except (ValueError, urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            print(
                f"[WARN] {result_path.name} attempt {attempt}/{max_retries} failed: {last_error}",
                file=sys.stderr,
            )
            if attempt < max_retries:
                time.sleep(min(5 * attempt, 15))

    raise RuntimeError(f"Failed to judge {result_path.name}: {last_error}")


def main() -> int:
    feature_path = FEATURE_JSON
    result_dir = DIR_PATH

    if not API_KEY:
        print("Missing API key. Set --api-key or OPENAI_API_KEY.", file=sys.stderr)
        return 1

    if not feature_path.exists():
        print(f"feature_path not found: {feature_path}", file=sys.stderr)
        return 1

    if not result_dir.exists() or not result_dir.is_dir():
        print(f"dir_path not found or not a directory: {result_dir}", file=sys.stderr)
        return 1

    tasks_by_id, task_text_to_id = load_merged_tasks(feature_path)
    result_files = collect_result_files(result_dir, TASK_IDS)

    if not result_files:
        print("No task result files found to judge.", file=sys.stderr)
        return 1

    output_path = (
        OUTPUT_PATH
        if OUTPUT_PATH
        else result_dir / f"judge_results-{model_slug(MODEL)}.json"
    )

    existing_results: Dict[str, Any] = {}
    if RESUME and output_path.exists():
        loaded = load_json(output_path)
        if isinstance(loaded, dict):
            existing_results = loaded

    print(f"[INFO] merged tasks loaded: {len(tasks_by_id)}")
    print(f"[INFO] result files to judge: {len(result_files)}")
    print(f"[INFO] output: {output_path}")

    results = dict(existing_results)
    for idx, result_path in enumerate(result_files, start=1):
        task_id = result_path.stem
        if RESUME and task_id in results:
            print(f"[SKIP] {task_id} already exists in output")
            continue

        print(f"[JUDGE] {idx}/{len(result_files)} {task_id}")
        judged = judge_one(
            result_path=result_path,
            tasks_by_id=tasks_by_id,
            task_text_to_id=task_text_to_id,
            model=MODEL,
            api_key=API_KEY,
            base_url=BASE_URL,
            temperature=TEMPERATURE,
            max_retries=MAX_RETRIES,
        )
        results[task_id] = judged
        save_json(output_path, results)

        if SLEEP_SECONDS > 0:
            time.sleep(SLEEP_SECONDS)

    print(f"[DONE] Saved judge results to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
