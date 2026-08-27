from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class TextRegion:
    text: str
    confidence: float
    box: Tuple[int, int, int, int]


@dataclass(frozen=True)
class VisionResult:
    scene: str
    text: str
    confidence: float
    regions: Tuple[TextRegion, ...] = ()


class VisionEngine:
    """Optional OCR adapter; unavailable OCR never prevents application startup."""

    def __init__(self, language: str = "chi_sim+eng") -> None:
        self.language = language

    def analyze(self, image: object) -> VisionResult:
        if image is None:
            return VisionResult("unknown", "", 0.0)
        try:
            import pytesseract  # type: ignore
        except ImportError:
            return VisionResult("unknown", "", 0.0)
        try:
            data = pytesseract.image_to_data(image, lang=self.language, output_type=pytesseract.Output.DICT)
        except Exception:
            return VisionResult("unknown", "", 0.0)
        regions: List[TextRegion] = []
        for i, raw in enumerate(data.get("text", [])):
            text = str(raw).strip()
            if not text:
                continue
            try:
                confidence = float(data.get("conf", ["-1"])[i]) / 100.0
                box = (int(data["left"][i]), int(data["top"][i]), int(data["width"][i]), int(data["height"][i]))
            except (ValueError, IndexError, KeyError):
                continue
            regions.append(TextRegion(text, max(0.0, min(1.0, confidence)), box))
        joined = " ".join(r.text for r in regions)
        return VisionResult("unknown", joined, max((r.confidence for r in regions), default=0.0), tuple(regions))
