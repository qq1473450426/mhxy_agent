from __future__ import annotations

from typing import Any

from .vision import TextRegion, VisionEngine, VisionResult


class TaskPanelOCR:
    """OCR adapter for the in-game right-side task tracker.

    The lower-left chat box is deliberately excluded because it produces many
    unrelated OCR hits and can contain words such as 师门/师父 in chat.
    Coordinates returned by this class remain in the original screenshot space.
    """

    def __init__(self, x_ratio: float = 0.58, y_ratio: float = 0.18) -> None:
        self.x_ratio = x_ratio
        self.y_ratio = y_ratio
        self.engine = VisionEngine()

    def analyze(self, image: Any) -> VisionResult:
        if image is None:
            return VisionResult("task_panel", "", 0.0)
        width, height = image.size
        x0 = max(0, min(width - 1, int(width * self.x_ratio)))
        y0 = max(0, min(height - 1, int(height * self.y_ratio)))
        crop = image.crop((x0, y0, width, height))
        result = self.engine.analyze(crop)
        regions = tuple(
            TextRegion(
                r.text,
                r.confidence,
                (r.box[0] + x0, r.box[1] + y0, r.box[2], r.box[3]),
            )
            for r in result.regions
        )
        return VisionResult("task_panel", result.text, result.confidence, regions)
