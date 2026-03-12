import os
import re
import json
import pandas as pd

from Prompt import Code
from utils import llm

def analyze_code_quality(code_path, task):
    with open(code_path, 'r', encoding='utf-8') as f:
        code = f.read()
    content = Code.prompt.format(task=task, code=code)
    result = llm.get_llm_evaluation(content)
    return result

def read_task(task_path):
    try:
        with open(task_path, 'r', encoding='utf-8') as f:
            tasks = [line.strip() for line in f.readlines() if line.strip()]
        return tasks
    except FileNotFoundError:
        return []
    except Exception as e:
        return []

def collect_results_for_df(dir_path, task_path):
    print(f"dir: {dir_path}")
    print(f"tasl: {task_path}")

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
    columns = ['Consistency', 'Readability', 'Efficiency']


    for idx, folder_name in enumerate(instruction_folders):
        folder_path = os.path.join(dir_path, folder_name)
        code_file_path = os.path.join(folder_path, 'firstcode.txt')   #todo

        if not os.path.exists(code_file_path):
            all_results_data.append([folder_name, 'N/A', 'N/A', 'N/A'])
            continue

        task = tasks[idx] if idx < len(tasks) else "none"
        result = analyze_code_quality(code_file_path, task)
        print(f".....{code_file_path}  {task}")


        print(f"[{folder_name}]:\n{result}\n")

        try:
            if isinstance(result, str):
                result_json = json.loads(result)
            elif isinstance(result, dict):
                result_json = result
            else:
                result_json = {}
        except json.JSONDecodeError:
            result_json = {}

        consistency = result_json.get("Consistency", {}).get("score", "N/A")
        readability = result_json.get("Readability", {}).get("score", "N/A")
        efficiency = result_json.get("Efficiency", {}).get("score", "N/A")

        all_results_data.append([folder_name, consistency, readability, efficiency])

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
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 2000)
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.expand_frame_repr', False)
        print(df_results)
