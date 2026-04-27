from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from ..agents.programmer import ProgrammerAgent
from ..agents.Tester import TesterAgent
from ..state import CodeGenState


def _set_solo_mode(_: CodeGenState) -> dict:
    """第一次进入 programmer 时，使用 solo 模式。"""
    return {"programmer_mode": "solo"}


def _set_test_mode(_: CodeGenState) -> dict:
    """进入 tester 驱动的修订阶段后，programmer 使用 test 模式。"""
    return {"programmer_mode": "test"}


def _route_after_programmer(state: CodeGenState) -> str:
    """
    programmer 执行后的路由：
    - 如果已经达到最大迭代次数，直接结束
    - 否则进入 tester
    """
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 1)

    if iteration >= max_iterations:
        return "end"

    return "tester"


def _route_after_tester(state: CodeGenState) -> str:
    """
    tester 执行后的路由：
    - 如果 need_revision 为 False，结束
    - 如果 need_revision 为 True，回到 programmer 继续修订
    """
    need_revision = state.get("need_revision", False)

    if not need_revision:
        return "end"

    return "set_test_mode"


def build_programmer_tester_graph(
    model_name: str,
    temperature: float = 0.0,
):
    """
    工作流：
    START -> set_solo_mode -> programmer
    programmer -> (iteration >= max_iterations ? END : tester)
    tester -> (need_revision == False ? END : set_test_mode)
    set_test_mode -> programmer
    """
    builder = StateGraph(CodeGenState)

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

    builder.add_node("set_solo_mode", _set_solo_mode)
    builder.add_node("set_test_mode", _set_test_mode)
    builder.add_node("programmer", programmer)
    builder.add_node("tester", tester)

    builder.add_edge(START, "set_solo_mode")
    builder.add_edge("set_solo_mode", "programmer")

    builder.add_conditional_edges(
        "programmer",
        _route_after_programmer,
        {
            "tester": "tester",
            "end": END,
        },
    )

    builder.add_conditional_edges(
        "tester",
        _route_after_tester,
        {
            "set_test_mode": "set_test_mode",
            "end": END,
        },
    )

    builder.add_edge("set_test_mode", "programmer")

    return builder.compile()