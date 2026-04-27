from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from ..agents.programmer import ProgrammerAgent
from ..agents.Reviewer import ReviewerAgent
from ..state import CodeGenState


def _set_solo_mode(_: CodeGenState) -> dict:
    """第一次进入 programmer 时，使用 solo 模式。"""
    return {"programmer_mode": "solo"}


def _set_review_mode(_: CodeGenState) -> dict:
    """进入修订阶段后，programmer 使用 review 模式。"""
    return {"programmer_mode": "review"}


def _route_after_programmer(state: CodeGenState) -> str:
    """
    programmer 执行后的路由：
    - 如果已经达到最大迭代次数，直接结束
    - 否则进入 reviewer
    """
    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 1)

    if iteration >= max_iterations:
        return "end"

    return "reviewer"


def _route_after_reviewer(state: CodeGenState) -> str:
    """
    reviewer 执行后的路由：
    - 如果 need_revision 为 False，结束
    - 如果 need_revision 为 True，回到 programmer 继续修订
    """
    need_revision = state.get("need_revision", False)

    if not need_revision:
        return "end"

    return "set_review_mode"


def build_programmer_reviewer_graph(
    model_name: str,
    temperature: float = 0.0,
):
    """
    工作流：
    START -> set_solo_mode -> programmer
    programmer -> (iteration >= max_iterations ? END : reviewer)
    reviewer -> (need_revision == False ? END : set_review_mode)
    set_review_mode -> programmer
    """
    builder = StateGraph(CodeGenState)

    programmer = ProgrammerAgent(
        agent_name="programmer",
        model_name=model_name,
        temperature=temperature,
    )

    reviewer = ReviewerAgent(
        agent_name="reviewer",
        model_name=model_name,
        temperature=temperature,
    )

    builder.add_node("set_solo_mode", _set_solo_mode)
    builder.add_node("set_review_mode", _set_review_mode)
    builder.add_node("programmer", programmer)
    builder.add_node("reviewer", reviewer)

    builder.add_edge(START, "set_solo_mode")
    builder.add_edge("set_solo_mode", "programmer")

    builder.add_conditional_edges(
        "programmer",
        _route_after_programmer,
        {
            "reviewer": "reviewer",
            "end": END,
        },
    )

    builder.add_conditional_edges(
        "reviewer",
        _route_after_reviewer,
        {
            "set_review_mode": "set_review_mode",
            "end": END,
        },
    )

    builder.add_edge("set_review_mode", "programmer")

    return builder.compile()