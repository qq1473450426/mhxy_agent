from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Tuple

from .vision import VisionEngine, VisionResult
from .yolo_detector import Detection, YoloDetector


@dataclass(frozen=True)
class FusedTarget:
    label: str
    confidence: float
    box: Tuple[int, int, int, int]
    ocr_text: str = ""


@dataclass(frozen=True)
class VisionFusionResult:
    yolo: Tuple[Detection, ...]
    ocr: VisionResult
    targets: Tuple[FusedTarget, ...]


class VisionFusion:
    """OCR-first vision pipeline; YOLO is explicitly opt-in because it is expensive."""

    def __init__(self, model_path: str = "models/mhxy_yolo.pt") -> None:
        self.detector = YoloDetector(model_path=model_path)
        self.ocr = VisionEngine()

    def analyze(self, image: Any, use_yolo: bool = False) -> VisionFusionResult:
        # OCR is sufficient for the current mentor task-link target.
        ocr = self.ocr.analyze(image)
        detections: Tuple[Detection, ...] = ()
        if use_yolo:
            detections = tuple(self.detector.detect(image))
        targets: List[FusedTarget] = []
        for detection in detections:
            x, y, w, h = detection.box
            text_parts: List[str] = []
            for region in ocr.regions:
                rx, ry, rw, rh = region.box
                cx = rx + rw / 2
                cy = ry + rh / 2
                if x <= cx <= x + w and y <= cy <= y + h:
                    text_parts.append(region.text)
            targets.append(FusedTarget(detection.label, detection.confidence, detection.box, " ".join(text_parts)))
        return VisionFusionResult(detections, ocr, tuple(targets))
