from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from ..agents.planner import PlannerAgent
from ..agents.programmer import ProgrammerAgent
from ..state import CodeGenState


def _set_plan_mode(_: CodeGenState) -> dict:

    return {"programmer_mode": "plan"}


def build_planner_programmer_graph(
    model_name: str,
    temperature: float = 0.0,
):
    """
    START -> planner -> set_plan_mode -> programmer -> END
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

    builder.add_node("planner", planner)
    builder.add_node("set_plan_mode", _set_plan_mode)
    builder.add_node("programmer", programmer)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "set_plan_mode")
    builder.add_edge("set_plan_mode", "programmer")
    builder.add_edge("programmer", END)

    return builder.compile()