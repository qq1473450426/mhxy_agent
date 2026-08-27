"""Minimal vision abstraction for future OCR/template recognition."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VisionResult:
    scene: str
    text: str
    confidence: float


class VisionEngine:
    def analyze(self, image: object) -> VisionResult:
        # Deliberately conservative until game-specific templates/OCR are configured.
        return VisionResult(scene="unknown", text="", confidence=0.0)
