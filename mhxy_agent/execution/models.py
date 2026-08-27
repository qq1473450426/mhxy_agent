from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple


class ActionKind(str, Enum):
    OBSERVE = "observe"
    MOVE = "move"
    INTERACT = "interact"
    WAIT = "wait"


@dataclass(frozen=True)
class Action:
    kind: ActionKind
    description: str
    target: Optional[str] = None
    requires_confirmation: bool = False
    point: Optional[Tuple[int, int]] = None


@dataclass(frozen=True)
class Observation:
    scene: str
    task_text: str = ""
    npc: Optional[str] = None
    position: Optional[str] = None


@dataclass(frozen=True)
class Verification:
    success: bool
    message: str
