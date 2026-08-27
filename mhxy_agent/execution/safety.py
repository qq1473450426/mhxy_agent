from __future__ import annotations

from .models import Action, ActionKind


BLOCKED_KINDS = set()


def validate_action(action: Action) -> tuple[bool, str]:
    if action.kind in BLOCKED_KINDS:
        return False, "动作被安全策略阻止"
    if action.kind is ActionKind.MOVE and not action.target:
        return False, "移动动作缺少目标"
    if action.kind is ActionKind.INTERACT and not action.target:
        return False, "交互动作缺少目标"
    return True, "安全检查通过"
