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
    """Chinese OCR with RapidOCR first and Tesseract as an optional fallback."""

    def __init__(self, language: str = "chi_sim+eng") -> None:
        self.language = language
        self._rapid = None

    def _analyze_rapidocr(self, image: object) -> VisionResult:
        from rapidocr_onnxruntime import RapidOCR  # type: ignore

        if self._rapid is None:
            self._rapid = RapidOCR()
        result, _ = self._rapid(image)
        regions: List[TextRegion] = []
        for item in result or []:
            if len(item) < 3:
                continue
            points, raw_text, raw_score = item[0], str(item[1]).strip(), float(item[2])
            if not raw_text or not points:
                continue
            xs = [int(p[0]) for p in points]
            ys = [int(p[1]) for p in points]
            box = (min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
            regions.append(TextRegion(raw_text, max(0.0, min(1.0, raw_score)), box))
        joined = " ".join(r.text for r in regions)
        return VisionResult("unknown", joined, max((r.confidence for r in regions), default=0.0), tuple(regions))

    def _analyze_tesseract(self, image: object) -> VisionResult:
        import pytesseract  # type: ignore

        data = pytesseract.image_to_data(image, lang=self.language, output_type=pytesseract.Output.DICT)
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

    def analyze(self, image: object) -> VisionResult:
        if image is None:
            return VisionResult("unknown", "", 0.0)
        try:
            return self._analyze_rapidocr(image)
        except Exception:
            try:
                return self._analyze_tesseract(image)
            except Exception:
                return VisionResult("unknown", "", 0.0)
