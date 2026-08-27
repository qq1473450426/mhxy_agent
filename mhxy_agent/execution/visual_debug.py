from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageDraw, ImageFont

from .vision import TextRegion
from .yolo_detector import Detection


def render_debug(image: Any, detections: Iterable[Detection], ocr_regions: Iterable[TextRegion], output: str = "data/latest_vision.png") -> Path:
    """Render YOLO/OCR boxes for debugging without changing the source capture."""
    if image is None:
        raise ValueError("没有可视化的截图")
    canvas = image.convert("RGB").copy()
    draw = ImageDraw.Draw(canvas)
    for d in detections:
        x, y, w, h = d.box
        draw.rectangle((x, y, x + w, y + h), outline="red", width=3)
        draw.text((x, max(0, y - 18)), f"YOLO {d.label} {d.confidence:.0%}", fill="red")
    for r in ocr_regions:
        x, y, w, h = r.box
        draw.rectangle((x, y, x + w, y + h), outline="blue", width=2)
        draw.text((x, y + h), f"OCR {r.text} {r.confidence:.0%}", fill="blue")
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)
    return path
