from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from ..agents.planner import PlannerAgent
from ..agents.programmer import ProgrammerAgent
from ..agents.Tester import TesterAgent
from ..state import CodeGenState


def _set_plan_mode(_: CodeGenState) -> dict:
    """第一次进入 programmer 时，使用 plan 模式。"""
    return {"programmer_mode": "plan"}


def _set_test_mode(_: CodeGenState) -> dict:
    """进入修订阶段后，programmer 使用 test 模式。"""
    return {"programmer_mode": "test"}


def _route_after_tester(state: CodeGenState) -> str:
    """
    tester 执行后的路由：
    1. need_revision == False -> 结束
    2. need_revision == True -> 检查是否达到最大迭代次数
    """
    need_revision = state.get("need_revision", False)

    if not need_revision:
        return "end"

    return _check_iteration(state)


def _check_iteration(state: CodeGenState) -> str:
    """
    第二层判断：
    - 如果 programmer 已达到最大迭代次数 -> 结束
    - 否则切到 test 模式，继续让 programmer 修订
    """
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 1)

    if iteration >= max_iterations:
        return "end"

    return "set_test_mode"


def build_plan_programmer_tester_graph(
    model_name: str,
    temperature: float = 0.0,
):
    """
    工作流：
    START -> planner -> set_plan_mode -> programmer -> tester
    tester -> conditional route
    set_test_mode -> programmer
    """
    builder = StateGraph(CodeGenState)

    planner = PlannerAgent(
        agent_name="planner",
        model_name=model_name,
        temperature=temperature,
    )

    programmer = ProgrammerAgent(
        agent_name="programmer",
        model_name=model_name,
        temperature=temperature,
    )

    tester = TesterAgent(
        agent_name="tester",
        model_name=model_name,
        temperature=temperature,
    )

    builder.add_node("planner", planner)
    builder.add_node("set_plan_mode", _set_plan_mode)
    builder.add_node("set_test_mode", _set_test_mode)
    builder.add_node("programmer", programmer)
    builder.add_node("tester", tester)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "set_plan_mode")
    builder.add_edge("set_plan_mode", "programmer")
    builder.add_edge("programmer", "tester")

    builder.add_conditional_edges(
        "tester",
        _route_after_tester,
        {
            "end": END,
            "set_test_mode": "set_test_mode",
        },
    )

    builder.add_edge("set_test_mode", "programmer")

    return builder.compile()