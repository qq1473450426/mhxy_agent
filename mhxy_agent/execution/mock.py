from __future__ import annotations

from .models import Action, ActionKind, Observation, Verification


class MockExecutor:
    """Deterministic simulator used before any real Windows integration."""

    def __init__(self) -> None:
        self.position = "长安城"
        self.task_active = False
        self.step = 0

    def observe(self) -> Observation:
        if not self.task_active:
            return Observation(scene="city", position=self.position)
        return Observation(
            scene="school_task",
            task_text="请完成师门任务",
            npc="师门使者",
            position=self.position,
        )

    def execute(self, action: Action) -> Verification:
        self.step += 1
        if action.kind is ActionKind.OBSERVE:
            return Verification(True, "观察完成")
        if action.kind is ActionKind.MOVE:
            if not action.target:
                return Verification(False, "移动目标为空")
            self.position = action.target
            return Verification(True, f"已到达 {action.target}")
        if action.kind is ActionKind.INTERACT:
            self.task_active = True
            return Verification(True, f"已交互：{action.target or '目标'}")
        if action.kind is ActionKind.WAIT:
            return Verification(True, "等待完成")
        return Verification(False, "未知动作")
