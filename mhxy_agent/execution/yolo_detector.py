from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Tuple


@dataclass(frozen=True)
class Detection:
    label: str
    confidence: float
    box: Tuple[int, int, int, int]


class YoloDetector:
    """Optional YOLO detector. The desktop app remains usable without weights."""

    def __init__(self, model_path: str = "models/mhxy_yolo.pt", confidence: float = 0.45) -> None:
        self.model_path = Path(model_path)
        self.confidence = confidence
        self._model: Optional[Any] = None
        self.error: str = ""

    @property
    def available(self) -> bool:
        return self.model_path.exists()

    def load(self) -> bool:
        if not self.available:
            self.error = f"YOLO模型不存在：{self.model_path}"
            return False
        try:
            from ultralytics import YOLO  # type: ignore
            self._model = YOLO(str(self.model_path))
            self.error = ""
            return True
        except Exception as exc:
            self.error = f"YOLO加载失败：{exc}"
            return False

    def detect(self, image: Any) -> List[Detection]:
        if image is None:
            return []
        if self._model is None and not self.load():
            return []
        try:
            results = self._model.predict(source=image, conf=self.confidence, verbose=False)
            detections: List[Detection] = []
            for result in results:
                names = getattr(result, "names", {})
                boxes = getattr(result, "boxes", None)
                if boxes is None:
                    continue
                xyxy = boxes.xyxy.cpu().tolist()
                confs = boxes.conf.cpu().tolist()
                classes = boxes.cls.cpu().tolist()
                for box, score, cls_id in zip(xyxy, confs, classes):
                    x1, y1, x2, y2 = [int(v) for v in box]
                    label = str(names.get(int(cls_id), int(cls_id)))
                    detections.append(Detection(label, float(score), (x1, y1, x2 - x1, y2 - y1)))
            return detections
        except Exception as exc:
            self.error = f"YOLO推理失败：{exc}"
            return []
