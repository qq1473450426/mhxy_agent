from __future__ import annotations

from .models import Action, ActionKind, Observation


class MentorPlanner:
    """First-step mentor-task planner. It only emits one safe action at a time."""

    def next_action(self, observation: Observation) -> Action:
        if observation.scene == "city" and not observation.task_text:
            return Action(ActionKind.INTERACT, "与师门使者交互", target="师门使者")
        if observation.scene == "school_task":
            return Action(ActionKind.WAIT, "等待下一步师门任务信息")
        return Action(ActionKind.OBSERVE, "重新观察当前场景")
