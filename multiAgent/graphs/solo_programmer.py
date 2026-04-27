from __future__ import annotations

from langgraph.graph import StateGraph, START, END

from ..agents.programmer import ProgrammerAgent
from ..state import CodeGenState


def build_solo_programmer_graph(
    model_name: str,
    temperature: float = 0.0,
):
    """
    START -> programmer -> END
    """
    builder = StateGraph(CodeGenState)

    programmer = ProgrammerAgent(
        agent_name="programmer",
        model_name=model_name,
        temperature=temperature,
    )

    builder.add_node("programmer", programmer)
    builder.add_edge(START, "programmer")
    builder.add_edge("programmer", END)

    return builder.compile()