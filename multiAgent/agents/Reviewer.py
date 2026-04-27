from __future__ import annotations

import json
from typing import Any

from .base_agent import BaseAgent
from ..state import AgentMetric, CodeGenState
from ..prompt.Reviewer import reviewerPrompt


class ReviewerAgent(BaseAgent):
    """读取最新代码并生成 review 结果的 Agent。"""

    def _latest(self, items: list[str] | None) -> str:
        if not items:
            return ""
        return items[-1].strip()

    def build_messages(self, state: CodeGenState) -> list[dict[str, str]]:
        """
        reviewer 读取：
        - task
        - 最新一版 code
        """
        latest_code = self._latest(state.get("codes"))
        if not latest_code:
            raise ValueError("ReviewerAgent requires at least one code in state['codes'].")

        prompt = reviewerPrompt.format(
            task=state["task"],
            code=latest_code,
        )

        return [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "Please review the code and return the result as JSON."},
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

    def _extract_review_result(self, text: str) -> tuple[bool, str]:
        """
        解析 reviewer 输出：
        {
          "need_revision": true,
          "review": "..."
        }
        """
        cleaned = self._strip_code_fence(text)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Reviewer output is not valid JSON: {e}") from e

        if not isinstance(data, dict):
            raise ValueError("Reviewer output must be a JSON object.")

        if "need_revision" not in data:
            raise ValueError("Reviewer output must contain 'need_revision'.")
        if "review" not in data:
            raise ValueError("Reviewer output must contain 'review'.")

        need_revision = data["need_revision"]
        review = data["review"]

        if not isinstance(need_revision, bool):
            raise ValueError("'need_revision' must be a boolean.")
        if not isinstance(review, str):
            raise ValueError("'review' must be a string.")

        return need_revision, review.strip()

    def build_state_update(
        self,
        state: CodeGenState,
        response_text: str,
        metric: AgentMetric,
    ) -> dict[str, Any]:
        need_revision, review = self._extract_review_result(response_text)
        update = {
            "reviews": state.get("reviews", []) + [review],
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
