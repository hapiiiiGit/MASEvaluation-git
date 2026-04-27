from __future__ import annotations

import json
from typing import Any

from .base_agent import BaseAgent
from ..state import AgentMetric, CodeGenState
from ..prompt.Tester import testerPrompt


class TesterAgent(BaseAgent):
    """读取最新代码并生成测试反馈 / 测试用例的 Agent。"""

    def _latest(self, items: list[str] | None) -> str:
        if not items:
            return ""
        return items[-1].strip()

    def build_messages(self, state: CodeGenState) -> list[dict[str, str]]:
        """
        tester 读取：
        - task
        - 最新一版 code
        """
        latest_code = self._latest(state.get("codes"))
        if not latest_code:
            raise ValueError("TesterAgent requires at least one code in state['codes'].")

        prompt = testerPrompt.format(
            task=state["task"],
            code=latest_code,
        )

        return [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "Please test the code and return the result as JSON."},
        ]

    def _strip_code_fence(self, text: str) -> str:
        """去掉偶发的 ```json / ``` 包裹。"""
        text = text.strip()
        if not text.startswith("```"):
            return text

        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        return "\n".join(lines).strip()

    def _extract_test_result(self, text: str) -> tuple[bool, str]:
        """
        解析 tester 输出：
        {
          "need_revision": true,
          "test_cases": "..."
        }
        """
        cleaned = self._strip_code_fence(text)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Tester output is not valid JSON: {e}") from e

        if not isinstance(data, dict):
            raise ValueError("Tester output must be a JSON object.")

        if "need_revision" not in data:
            raise ValueError("Tester output must contain 'need_revision'.")
        if "test_cases" not in data:
            raise ValueError("Tester output must contain 'test_cases'.")

        need_revision = data["need_revision"]
        test_cases = data["test_cases"]

        if not isinstance(need_revision, bool):
            raise ValueError("'need_revision' must be a boolean.")
        if not isinstance(test_cases, str):
            raise ValueError("'test_cases' must be a string.")

        return need_revision, test_cases.strip()

    def build_state_update(
        self,
        state: CodeGenState,
        response_text: str,
        metric: AgentMetric,
    ) -> dict[str, Any]:
        need_revision, test_cases = self._extract_test_result(response_text)
        update = {
            "test_cases": state.get("test_cases", []) + [test_cases],
            "need_revision": need_revision,
            "metrics": [metric],
            "success": True,
            "error": "",
        }

        if not need_revision:
            latest_code = self._latest(state.get("codes"))
            if latest_code:
                update["final_code"] = latest_code

        return update
