from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ActionKind(str, Enum):
    OBSERVE = "observe"
    MOVE = "move"
    INTERACT = "interact"
    WAIT = "wait"


@dataclass(frozen=True)
class Action:
    kind: ActionKind
    description: str
    target: str | None = None
    requires_confirmation: bool = False


@dataclass(frozen=True)
class Observation:
    scene: str
    task_text: str = ""
    npc: str | None = None
    position: str | None = None


@dataclass(frozen=True)
class Verification:
    success: bool
    message: str
