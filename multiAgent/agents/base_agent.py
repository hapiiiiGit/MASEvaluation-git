from __future__ import annotations

from abc import ABC, abstractmethod
from time import perf_counter
from typing import Any

from openai import OpenAI

from ..state import AgentMetric, CodeGenState
from ..config.setting import settings


class BaseAgent(ABC):
    def __init__(
        self,
        agent_name: str,
        model_name: str,
        temperature: float = 0.0,
    ) -> None:
        self.agent_name = agent_name
        self.model_name = model_name
        self.temperature = temperature

        self.client = OpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
        )

    @abstractmethod
    def build_messages(self, state: CodeGenState) -> list[dict[str, str]]:
        raise NotImplementedError

    @abstractmethod
    def build_state_update(
        self,
        state: CodeGenState,
        response_text: str,
        metric: AgentMetric,
    ) -> dict[str, Any]:
        raise NotImplementedError

    def _next_call_index(self, state: CodeGenState) -> int:
        metrics = state.get("metrics", [])
        return 1 + sum(1 for m in metrics if m.get("agent") == self.agent_name)

    def _usage_to_metric(
        self,
        state: CodeGenState,
        usage_metadata: dict[str, int],
        wall_time_s: float,
        success: bool,
        error: str = "",
    ) -> AgentMetric:
        input_tokens = int(usage_metadata.get("input_tokens", 0))
        output_tokens = int(usage_metadata.get("output_tokens", 0))
        total_tokens = int(usage_metadata.get("total_tokens", 0))

        return {
            "agent": self.agent_name,
            "model": self.model_name,
            "run_name": self.agent_name,
            "call_index": self._next_call_index(state),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "wall_time_s": wall_time_s,
            "success": success,
            "error": error,
        }

    def __call__(self, state: CodeGenState) -> dict[str, Any]:
        start = perf_counter()

        try:
            messages = self.build_messages(state)
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=self.temperature,
                response_format={"type": "json_object"},
            )

            elapsed = perf_counter() - start
            usage = response.usage
            metric = self._usage_to_metric(
                state=state,
                usage_metadata={
                    "input_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
                    "output_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
                    "total_tokens": getattr(usage, "total_tokens", 0) if usage else 0,
                },
                wall_time_s=elapsed,
                success=True,
            )

            response_text = (response.choices[0].message.content or "").strip()

            return self.build_state_update(state, response_text, metric)

        except Exception as e:
            elapsed = perf_counter() - start
            metric = self._usage_to_metric(
                state=state,
                usage_metadata={},
                wall_time_s=elapsed,
                success=False,
                error=str(e),
            )
            return {
                "metrics": [metric],
                "success": False,
                "error": str(e),
            }
