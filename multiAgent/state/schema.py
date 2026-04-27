from __future__ import annotations

import operator
from typing import Optional
from typing_extensions import Annotated, TypedDict


class AgentMetric(TypedDict, total=False):
    """单次 agent 执行的监控记录。"""

    agent: str                 # planner / programmer / reviewer / tester
    model: str                 # 例如 gpt-4.1
    run_name: str              # 方便 tracing / 日志区分
    call_index: int            # 该 agent 第几次调用

    input_tokens: int
    output_tokens: int
    total_tokens: int
    wall_time_s: float         # 真实经过时间（秒）

    success: bool
    error: str


class InputState(TypedDict):
    """图的输入状态：只保留任务本身。"""

    task_id: str
    task: str


class WorkState(TypedDict, total=False):
    """代码生成过程中的中间产物。"""

    plans: list[str]
    codes: list[str]
    reviews: list[str]
    test_cases: list[str]
    final_code: Optional[str]

    # 控制流字段
    iteration: int              # 从 0 开始，programmer 每执行一次 +1
    max_iterations: int         # 最大允许迭代次数
    need_revision: bool
    programmer_mode: str        # "solo" / "plan" / "review" / "test"


class MonitorState(TypedDict, total=False):
    """监控相关状态。"""

    metrics: Annotated[list[AgentMetric], operator.add]


class OutputState(TypedDict, total=False):
    """图最终输出给外部的结果。"""

    final_code: str
    metrics: list[AgentMetric]
    success: bool
    error: str


class CodeGenState(InputState, WorkState, MonitorState, total=False):
    """图内部共享的完整状态。"""

    success: bool
    error: str