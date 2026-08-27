from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from PIL import Image, ImageDraw, ImageFont

from .vision import TextRegion
from .yolo_detector import Detection


def _font(size: int = 16) -> ImageFont.ImageFont:
    """Prefer common Windows CJK fonts so Chinese OCR labels render correctly."""
    candidates = (
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\simsun.ttc",
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_debug(image: Any, detections: Iterable[Detection], ocr_regions: Iterable[TextRegion], output: str = "data/latest_vision.png") -> Path:
    """Render YOLO/OCR boxes for debugging without changing the source capture."""
    if image is None:
        raise ValueError("没有可视化的截图")
    canvas = image.convert("RGB").copy()
    draw = ImageDraw.Draw(canvas)
    font = _font()
    for d in detections:
        x, y, w, h = d.box
        draw.rectangle((x, y, x + w, y + h), outline="red", width=3)
        draw.text((x, max(0, y - 20)), f"YOLO {d.label} {d.confidence:.0%}", fill="red", font=font)
    for r in ocr_regions:
        x, y, w, h = r.box
        draw.rectangle((x, y, x + w, y + h), outline="blue", width=2)
        draw.text((x, min(canvas.height - 18, y + h)), f"OCR {r.text} {r.confidence:.0%}", fill="blue", font=font)
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)
    return path
