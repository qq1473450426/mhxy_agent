from __future__ import annotations

from dataclasses import dataclass, field

HIGH_RISK_ACTIONS = {"DELETE_CHARACTER", "DELETE_HIGH_VALUE_ITEM", "HIGH_VALUE_TRADE", "IRREVERSIBLE"}

@dataclass
class ActionStep:
    action: str
    observe: str
    verify: str
    args: dict = field(default_factory=dict)

class SafetyGuard:
    def __init__(self, explicitly_allowed: set[str] | None = None) -> None:
        self.explicitly_allowed = explicitly_allowed or set()

    def check(self, action: str) -> tuple[bool, str]:
        if action in HIGH_RISK_ACTIONS and action not in self.explicitly_allowed:
            return False, "需要用户明确授权的高风险或不可逆操作"
        return True, "允许"

class ActionPlanner:
    def __init__(self, guard: SafetyGuard | None = None) -> None:
        self.guard = guard or SafetyGuard()

    def make(self, task: str) -> list[ActionStep]:
        templates = {
            "抓鬼": [
                ("CHECK_TEAM", "TEAM_VISIBLE", "TEAM_VISIBLE == TRUE"),
                ("CHECK_CHARACTER_STATE", "ALL_CHARACTERS_READY", "ALL_CHARACTERS_READY == TRUE"),
                ("ACCEPT_TASK", "TASK_ACCEPTED", "TASK_ACCEPTED == TRUE"),
                ("LOCATE_TARGET", "TARGET_FOUND", "TARGET_FOUND == TRUE"),
                ("NAVIGATE", "TARGET_LOCATION", "TARGET_LOCATION == TRUE"),
                ("ENTER_BATTLE", "BATTLE_VISIBLE", "BATTLE_VISIBLE == TRUE"),
                ("EXECUTE_BATTLE", "BATTLE_RESULT", "BATTLE_RESULT in {SUCCESS,FAILURE}"),
                ("VERIFY_REWARD", "REWARD_VISIBLE", "REWARD_VISIBLE == TRUE"),
            ]
        }
        rows = templates.get(task, [
            ("CHECK_STATE", "STATE_VISIBLE", "STATE_VISIBLE == TRUE"),
            ("EXECUTE_TASK", "TASK_RESULT", "TASK_RESULT == TRUE"),
        ])
        result = []
        for action, observe, verify in rows:
            ok, reason = self.guard.check(action)
            if not ok:
                raise PermissionError(reason)
            result.append(ActionStep(action, observe, verify))
        return result
