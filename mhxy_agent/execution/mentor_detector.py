from __future__ import annotations

from typing import Any, Optional

from .models import Action, ActionKind
from .vision import TextRegion, VisionResult


class MentorTargetDetector:
    """Find the clickable red task-link in the in-game task panel.

    In the supplied client UI, the actionable target is not the NPC sprite.
    The task panel contains a red underlined word (e.g. "师父"); clicking that
    link opens the dialogue. We therefore prefer a red-text target inside an
    OCR region containing a mentor keyword, then fall back to OCR coordinates.
    """

    KEYWORDS = ("师父", "师傅", "师门使者", "门派师傅")

    def detect(self, vision: VisionResult, image: Any = None) -> Optional[Action]:
        region = self._best_keyword_region(vision.regions)
        if region is not None and image is not None:
            red_box = self._red_box_in_region(image, region)
            if red_box is not None:
                x, y, w, h = red_box
                return Action(
                    ActionKind.INTERACT,
                    f"识别到师门任务红色链接：{region.text} ({region.confidence:.0%})",
                    target=region.text,
                    point=(x + w // 2, y + h // 2),
                )

        if region is None:
            return None
        x, y, w, h = region.box
        return Action(
            ActionKind.INTERACT,
            f"识别到师门任务文字：{region.text} ({region.confidence:.0%})",
            target=region.text,
            point=(x + w // 2, y + h // 2),
        )

    def _best_keyword_region(self, regions: tuple[TextRegion, ...]) -> Optional[TextRegion]:
        matches = [r for r in regions if any(k in r.text for k in self.KEYWORDS)]
        if not matches:
            return None
        # Prefer the right-side task-panel region when several OCR hits exist.
        matches.sort(key=lambda r: (r.box[0] < 0, -r.confidence), reverse=False)
        return max(matches, key=lambda r: r.confidence)

    @staticmethod
    def _red_box_in_region(image: Any, region: TextRegion) -> Optional[tuple[int, int, int, int]]:
        try:
            rgb = image.convert("RGB")
            x, y, w, h = region.box
            if w <= 0 or h <= 0:
                return None
            # Expand slightly because OCR boxes can be tighter than the colored glyphs.
            pad = 4
            x0, y0 = max(0, x - pad), max(0, y - pad)
            x1, y1 = min(rgb.width, x + w + pad), min(rgb.height, y + h + pad)
            crop = rgb.crop((x0, y0, x1, y1))
            px = crop.load()
            coords = []
            for yy in range(crop.height):
                for xx in range(crop.width):
                    r, g, b = px[xx, yy]
                    # Red task links are saturated red; tolerate anti-aliasing.
                    if r >= 150 and r >= g * 1.45 and r >= b * 1.35:
                        coords.append((xx, yy))
            if len(coords) < 6:
                return None
            xs = [p[0] for p in coords]
            ys = [p[1] for p in coords]
            bx0, bx1 = min(xs), max(xs)
            by0, by1 = min(ys), max(ys)
            return (x0 + bx0, y0 + by0, bx1 - bx0 + 1, by1 - by0 + 1)
        except Exception:
            return None
