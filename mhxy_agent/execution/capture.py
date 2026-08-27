"""Best-effort Windows window capture with an optional Pillow dependency."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CaptureResult:
    ok: bool
    message: str
    image: object | None = None


class WindowCapture:
    def capture(self, handle: int) -> CaptureResult:
        try:
            import win32gui  # type: ignore
            from PIL import ImageGrab  # type: ignore
        except ImportError as exc:
            return CaptureResult(False, f"缺少截图依赖：{exc}")

        try:
            left, top, right, bottom = win32gui.GetWindowRect(handle)
            if right <= left or bottom <= top:
                return CaptureResult(False, "窗口尺寸无效")
            image = ImageGrab.grab(bbox=(left, top, right, bottom), all_screens=True)
            return CaptureResult(True, "截图成功", image)
        except Exception as exc:
            return CaptureResult(False, f"截图失败：{exc}")
