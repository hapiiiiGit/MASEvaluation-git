from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from ..agents.planner import PlannerAgent
from ..agents.programmer import ProgrammerAgent
from ..agents.Reviewer import ReviewerAgent
from ..state import CodeGenState


def _set_plan_mode(_: CodeGenState) -> dict:

    return {"programmer_mode": "plan"}


def _set_review_mode(_: CodeGenState) -> dict:

    return {"programmer_mode": "review"}


def _route_after_reviewer(state: CodeGenState) -> str:

    need_revision = state.get("need_revision", False)

    if not need_revision:
        return "end"

    return _check_iteration(state)


def _check_iteration(state: CodeGenState) -> str:

    iteration = state.get("iteration", 0)
    max_iterations = state.get("max_iterations", 1)

    if iteration >= max_iterations:
        return "end"

    return "set_review_mode"


def build_plan_programmer_reviewer_graph(
    model_name: str,
    temperature: float = 0.0,
):

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

    reviewer = ReviewerAgent(
        agent_name="reviewer",
        model_name=model_name,
        temperature=temperature,
    )

    builder.add_node("planner", planner)
    builder.add_node("set_plan_mode", _set_plan_mode)
    builder.add_node("set_review_mode", _set_review_mode)
    builder.add_node("programmer", programmer)
    builder.add_node("reviewer", reviewer)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "set_plan_mode")
    builder.add_edge("set_plan_mode", "programmer")
    builder.add_edge("programmer", "reviewer")

    builder.add_conditional_edges(
        "reviewer",
        _route_after_reviewer,
        {
            "end": END,
            "set_review_mode": "set_review_mode",
        },
    )

    builder.add_edge("set_review_mode", "programmer")

    return builder.compile()
