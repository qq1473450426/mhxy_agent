from __future__ import annotations

from typing import Optional, Tuple

from .models import Action, ActionKind
from .vision import VisionResult


class MentorTargetDetector:
    KEYWORDS = ("师门使者", "师门", "门派师傅", "师傅")

    def detect(self, vision: VisionResult) -> Optional[Action]:
        best = None
        for region in vision.regions:
            if any(keyword in region.text for keyword in self.KEYWORDS):
                score = region.confidence
                if best is None or score > best[0]:
                    x, y, w, h = region.box
                    best = (score, x + w // 2, y + h // 2, region.text)
        if best is None:
            return None
        score, x, y, text = best
        return Action(
            ActionKind.INTERACT,
            f"识别到师门目标：{text} ({score:.0%})",
            target=text,
            point=(x, y),
        )
