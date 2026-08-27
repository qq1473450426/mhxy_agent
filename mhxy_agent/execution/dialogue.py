from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .task_panel import TaskPanelOCR
from .vision import TextRegion, VisionResult


@dataclass(frozen=True)
class DialogueOption:
    text: str
    point: tuple[int, int]
    confidence: float
    box: tuple[int, int, int, int]


class DialogueDetector:
    """Detect clickable options in the bottom dialogue panel.

    The current mentor dialogue layout is a two-column option list. OCR is
    restricted to the dialogue panel so chat/scenery text is not considered.
    """

    KEYWORDS = ("师门任务", "交谈", "给与", "学习技能", "师门贡献兑换")

    def __init__(self) -> None:
        self.ocr = TaskPanelOCR(x_ratio=0.05, y_ratio=0.50)

    def analyze(self, image: object) -> VisionResult:
        return self.ocr.analyze(image)

    def find_option(self, result: VisionResult, keyword: str = "师门任务") -> Optional[DialogueOption]:
        candidates: list[TextRegion] = []
        for region in result.regions:
            text = region.text.replace(" ", "")
            if keyword in text:
                candidates.append(region)
        if not candidates:
            return None
        region = max(candidates, key=lambda r: r.confidence)
        x, y, w, h = region.box
        return DialogueOption(
            text=region.text,
            point=(x + w // 2, y + h // 2),
            confidence=region.confidence,
            box=region.box,
        )
