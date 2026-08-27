from __future__ import annotations

from typing import Optional

from .models import Action, ActionKind, Observation
from .vision import VisionResult


class MentorTargetDetector:
    """Resolve a safe interaction point from OCR regions.

    It deliberately requires an exact configurable keyword instead of guessing
    arbitrary screen coordinates.
    """

    def __init__(self, keywords: Optional[tuple[str, ...]] = None) -> None:
        self.keywords = keywords or ("师门使者", "师门")

    def find_target(self, result: VisionResult) -> Optional[tuple[int, int, str, float]]:
        for region in result.regions:
            if any(keyword in region.text for keyword in self.keywords):
                x, y, w, h = region.box
                return x + w // 2, y + h // 2, region.text, region.confidence
        return None


class MentorPlanner:
    """First-step mentor planner with optional vision target resolution."""

    def __init__(self) -> None:
        self.detector = MentorTargetDetector()

    def next_action(self, observation: Observation, vision: Optional[VisionResult] = None) -> Action:
        if observation.scene == "city" and not observation.task_text:
            if vision is not None:
                target = self.detector.find_target(vision)
                if target is not None:
                    x, y, text, confidence = target
                    return Action(
                        ActionKind.INTERACT,
                        f"交互 {text} @ ({x},{y})，置信度 {confidence:.0%}",
                        target=text,
                    )
            return Action(ActionKind.OBSERVE, "观察师门使者位置")
        if observation.scene == "school_task":
            return Action(ActionKind.WAIT, "等待下一步师门任务信息")
        return Action(ActionKind.OBSERVE, "重新观察当前场景")
