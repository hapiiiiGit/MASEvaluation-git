from __future__ import annotations

from torch.cuda import graph

from multiAgent.graphs.solo_programmer import build_solo_programmer_graph
from multiAgent.graphs.planner_programmer import build_planner_programmer_graph
from multiAgent.graphs.programmer_reviewer import build_programmer_reviewer_graph
from multiAgent.graphs.programmer_tester import build_programmer_tester_graph
from multiAgent.graphs.plan_programmer_reviewer import build_plan_programmer_reviewer_graph
from multiAgent.graphs.plan_programmer_tester import build_plan_programmer_tester_graph
from multiAgent.config.setting import settings


def main():
    ## solo programmer
    """
    graph = build_solo_programmer_graph(
        model_name=settings.model_name,
        temperature=settings.temperature,
    )

    init_state = {
        "task_id": "demo_001",
        "task": "Write a Python function that checks whether a string is a palindrome.",
        "codes": [],
        "plans": [],
        "reviews": [],
        "test_cases": [],
        "iteration": 0,
        "max_iterations": settings.max_iterations,
        "need_revision": False,
        "programmer_mode": settings.programmer_mode,
    }
    """
    # planner + programmer
    """
    graph = build_planner_programmer_graph(
        model_name=settings.model_name,
        temperature=settings.temperature,
    )

    init_state = {
        "task_id": "demo_002",
        "task": "Write a Python function that checks whether a string is a palindrome.",
        "codes": [],
        "plans": [],
        "reviews": [],
        "test_cases": [],
        "iteration": 0,
        "max_iterations":  settings.max_iterations,
        "need_revision": False,
        "programmer_mode": settings.programmer_mode,
    }
    """
    # reviewer + programmer
    """
    graph = build_programmer_reviewer_graph(
        model_name=settings.model_name,
        temperature=settings.temperature,
    )

    init_state = {
        "task_id": "demo_003",
        "task": "Please help me implement a headless Python script that scrapes data from https://www.loenoverblik.dk/ by iterating through all available periods and sector levels down to level 3, extracts 'Årsværk' data for each 'Personalekategori', and exports the results to a consistent file format, ensuring the script is automatic and respects the site's navigation logic.",
        "codes": [],
        "plans": [],
        "reviews": [],
        "test_cases": [],
        "iteration": 0,
        "max_iterations": settings.max_iterations,
    }
    """

    # tester + programmer
    """
    graph = build_programmer_tester_graph(
        model_name=settings.model_name,
        temperature=settings.temperature,
    )

    init_state = {
        "task_id": "demo_004",
        "task": "Please help me implement a headless Python script that scrapes data from https://www.loenoverblik.dk/ by iterating through all available periods and sector levels down to level 3, extracts 'Årsværk' data for each 'Personalekategori', and exports the results to a consistent file format, ensuring the script is automatic and respects the site's navigation logic.",
        "codes": [],
        "plans": [],
        "reviews": [],
        "test_cases": [],
        "iteration": 0,
        "max_iterations": settings.max_iterations,
        "need_revision": False,
    }
    """

    # planner + programmer + reviewer
    """
    graph = build_plan_programmer_reviewer_graph(
        model_name=settings.model_name,
        temperature=settings.temperature,
    )
    init_state = {
        "task_id": "demo_005",
        "task": "Write a Python function that checks whether a string is a palindrome.",
        "codes": [],
        "plans": [],
        "reviews": [],
        "test_cases": [],
        "iteration": 0,
        "max_iterations": 3,
        "need_revision": False,
    }
    """

    # planner + programmer + tester
    graph = build_plan_programmer_tester_graph(
        model_name=settings.model_name,
        temperature=settings.temperature,
    )
    init_state = {
        "task_id": "demo_005",
        "task": "Write a Python function that checks whether a string is a palindrome.",
        "codes": [],
        "plans": [],
        "reviews": [],
        "test_cases": [],
        "iteration": 0,
        "max_iterations": 3,
        "need_revision": False,
    }
    result = graph.invoke(init_state)

    print("\n===== FINAL CODE =====\n")
    print(result.get("final_code"))

    print("\n===== METRICS =====\n")
    for m in result.get("metrics", []):
        print(m)

    print("\n===== FULL RESULT =====\n")
    print(result)


if __name__ == "__main__":
    main()
