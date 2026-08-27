"""Fast Windows window capture with MSS and Pillow fallback."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class CaptureResult:
    ok: bool
    message: str
    image: Optional[object] = None


class WindowCapture:
    """Capture only the selected window; MSS is preferred for lower latency."""

    def __init__(self) -> None:
        self._mss = None

    def capture(self, handle: int) -> CaptureResult:
        try:
            import win32gui  # type: ignore
        except ImportError as exc:
            return CaptureResult(False, f"缺少窗口依赖：{exc}")

        try:
            left, top, right, bottom = win32gui.GetWindowRect(handle)
            if right <= left or bottom <= top:
                return CaptureResult(False, "窗口尺寸无效")
            width, height = right - left, bottom - top

            # MSS avoids ImageGrab's slower multi-screen path and keeps capture scoped.
            try:
                from mss import mss  # type: ignore
                from PIL import Image
                if self._mss is None:
                    self._mss = mss()
                shot = self._mss.grab({"left": left, "top": top, "width": width, "height": height})
                image = Image.frombytes("RGB", shot.size, shot.rgb)
                return CaptureResult(True, f"截图成功(MSS {width}x{height})", image)
            except Exception:
                from PIL import ImageGrab  # type: ignore
                image = ImageGrab.grab(bbox=(left, top, right, bottom), all_screens=True)
                return CaptureResult(True, f"截图成功(ImageGrab {width}x{height})", image)
        except Exception as exc:
            return CaptureResult(False, f"截图失败：{exc}")
