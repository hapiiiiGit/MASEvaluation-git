from __future__ import annotations

import json
from typing import Any

from .base_agent import BaseAgent
from ..state import AgentMetric, CodeGenState
from ..prompt.withPlan import withPlanPrompt
from ..prompt.withReview import withReviewPrompt
from ..prompt.withTest import withTestPrompt
from ..prompt.withProgrammerSolo import withProgrammerSoloPrompt


class ProgrammerAgent(BaseAgent):
    """根据 workflow / state 自动选择 prompt 的代码生成 Agent。"""

    def _latest(self, items: list[str] | None) -> str:
        if not items:
            return ""
        return items[-1].strip()

    def _select_prompt_mode(self, state: CodeGenState) -> str:
        """
        优先级：
        1. 显式指定 state["programmer_mode"]
        2. review
        3. test
        4. plan
        5. solo
        """
        explicit_mode = str(state.get("programmer_mode", "")).strip().lower()
        if explicit_mode in {"solo", "plan", "review", "test"}:
            return explicit_mode

        if self._latest(state.get("reviews")):
            return "review"
        if self._latest(state.get("test_cases")):
            return "test"
        if self._latest(state.get("plans")):
            return "plan"
        return "solo"

    def build_messages(self, state: CodeGenState) -> list[dict[str, str]]:
        """
        prompt 选择规则：
        - solo: system = withProgrammerSoloPrompt, user = task
        - plan: system = withPlanPrompt.format(plan=...),
        - review: system = withReviewPrompt.format(...), 无 user
        - test: system = withTestPrompt.format(...), 无 user
        """
        mode = self._select_prompt_mode(state)

        latest_plan = self._latest(state.get("plans"))
        latest_review = self._latest(state.get("reviews"))
        latest_test_cases = self._latest(state.get("test_cases"))
        previous_code = self._latest(state.get("codes"))

        if mode == "review":
            prompt = withReviewPrompt.format(
                previous_code=previous_code,
                review=latest_review,
            )
            return [
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Please return the revised code as JSON."},
            ]

        if mode == "test":
            prompt = withTestPrompt.format(
                previous_code=previous_code,
                test_cases=latest_test_cases,
            )
            return [
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Please return the revised code as JSON."},
            ]

        if mode == "plan":
            prompt = withPlanPrompt.format(
                plan=latest_plan,
                task=state["task"],
            )
            return [
                {"role": "system", "content": prompt},
                {"role": "user", "content": "Please implement the plan and return the code as JSON."},
            ]

        # solo
        return [
            {"role": "system", "content": withProgrammerSoloPrompt},
            {"role": "user", "content": state["task"]},
        ]

    def _strip_code_fence(self, text: str) -> str:
        text = text.strip()
        if not text.startswith("```"):
            return text

        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()

    def _try_extract_nested_code(self, text: str) -> str | None:
        text = text.strip()
        if not text:
            return None

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return None

        if isinstance(data, dict):
            if isinstance(data.get("code"), str):
                return data["code"]
            if isinstance(data.get("output"), str):
                nested = self._try_extract_nested_code(data["output"])
                if nested is not None:
                    return nested

        return None

    def _extract_code(self, text: str) -> str:
        cleaned = self._strip_code_fence(text)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            return cleaned.strip()

        if not isinstance(data, dict):
            raise ValueError("Programmer output must be a JSON object.")

        if isinstance(data.get("code"), str):
            code = data["code"].strip()
            nested = self._try_extract_nested_code(code)
            return nested.strip() if nested is not None else code

        if isinstance(data.get("output"), str):
            nested = self._try_extract_nested_code(data["output"])
            if nested is not None:
                return nested.strip()
            return data["output"].strip()

        raise ValueError("Programmer output does not contain a valid 'code' field.")

    def build_state_update(
        self,
        state: CodeGenState,
        response_text: str,
        metric: AgentMetric,
    ) -> dict[str, Any]:
        # print("tetsssssssssssssss")
        # print(response_text)
        code = self._extract_code(response_text)
        mode = self._select_prompt_mode(state)

        current_iteration = state.get("iteration", 0)
        next_iteration = current_iteration + 1
        max_iterations = state.get("max_iterations", 1)

        update = {
            "codes": state.get("codes", []) + [code],
            "iteration": next_iteration,
            "metrics": [metric],
            "success": True,
            "error": "",
        }

        # 规则1：solo / plan 直接视为 final_code
        if mode in {"solo", "plan"}:
            update["final_code"] = code

        # 规则2：review / test 只有达到最大迭代次数时才写 final_code
        elif mode in {"review", "test"} and next_iteration >= max_iterations:
            update["final_code"] = code

        return update
