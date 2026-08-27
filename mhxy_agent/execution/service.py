from __future__ import annotations

from .mentor import MentorPlanner
from .mock import MockExecutor
from .safety import validate_action


class ExecutionService:
    """Observe -> decide one action -> safety gate -> execute -> verify."""

    def __init__(self) -> None:
        self.executor = MockExecutor()
        self.planner = MentorPlanner()

    def step(self) -> dict[str, str | bool]:
        observation = self.executor.observe()
        action = self.planner.next_action(observation)
        allowed, safety_message = validate_action(action)
        if not allowed:
            return {
                "success": False,
                "stage": "safety",
                "message": safety_message,
            }
        verification = self.executor.execute(action)
        return {
            "success": verification.success,
            "stage": "verify",
            "message": verification.message,
            "action": action.description,
        }
