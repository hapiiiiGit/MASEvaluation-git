import os
import re
import json
import pandas as pd

from utils import llm
from Prompt import Plan


def read_task(task_path):
    try:
        with open(task_path, 'r', encoding='utf-8') as f:
            tasks = [line.strip() for line in f.readlines() if line.strip()]
        return tasks
    except FileNotFoundError:
        print(f"'{task_path}' not exist")
        return []
    except Exception as e:
        return []


def analyze_plan_quality(plan_path, task):
    with open(plan_path, 'r', encoding='utf-8') as f:
        plan = f.read()
    content = Plan.prompt.format(task=task, plan=plan)
    result = llm.get_llm_evaluation(content)
    return result


def collect_results_for_df(dir_path, task_path):
    print(f"dir: {dir_path}")

    if not os.path.isdir(dir_path):
        print(f"'{dir_path}' not exist")
        return None

    tasks = read_task(task_path)
    if not tasks:
        return None

    instruction_folders = [item for item in os.listdir(dir_path)
                           if os.path.isdir(os.path.join(dir_path, item)) and item.startswith('instruction')]
    instruction_folders.sort(key=lambda x: int(re.findall(r'\d+', x)[0]) if re.findall(r'\d+', x) else 0)

    if not instruction_folders:
        return None

    if len(tasks) != len(instruction_folders):
        print(f"task({len(tasks)}) & instruction num ({len(instruction_folders)}) not match")


    all_results_data = []
    columns = ['Completeness', 'Correctness', 'Clarity']


    for idx, folder_name in enumerate(instruction_folders):
        folder_path = os.path.join(dir_path, folder_name)
        plan_file_path = os.path.join(folder_path, 'plan.txt')  # todo

        if not os.path.exists(plan_file_path):
            all_results_data.append([folder_name, 'N/A', 'N/A', 'N/A'])
            continue

        if idx < len(tasks):
            task = tasks[idx]
        else:
            task = "N/A" 
        print(f".....{plan_file_path}  {task}")
        result = analyze_plan_quality(plan_file_path, task)

 
        print(f"\n[{folder_name}] row LLM JSON :\n{result}\n")


        try:
            if isinstance(result, str):
                result_json = json.loads(result)
            elif isinstance(result, dict):
                result_json = result
            else:
                result_json = {}
        except json.JSONDecodeError:
            result_json = {}

        completeness = result_json.get("Completeness", {}).get("score", "N/A")
        correctness = result_json.get("Correctness", {}).get("score", "N/A")
        clarity = result_json.get("Clarity", {}).get("score", "N/A")

        all_results_data.append([folder_name, completeness, correctness, clarity])

    df_columns = ['instruction'] + columns
    df = pd.DataFrame(all_results_data, columns=df_columns)

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    return df



if __name__ == '__main__':
    dir_path = ""
    task_path = ""
    df_results = collect_results_for_df(dir_path, task_path)

    if df_results is not None:
        print(df_results)
