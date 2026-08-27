from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int
    y: int


class WindowsInput:
    """Windows mouse input using coordinates relative to the captured window."""

    def click(self, handle: int, point: Point) -> tuple[bool, str]:
        try:
            import win32api  # type: ignore
            import win32con  # type: ignore
            import win32gui  # type: ignore
        except ImportError as exc:
            return False, f"缺少 Windows 输入依赖：{exc}"

        try:
            if not win32gui.IsWindow(handle):
                return False, "目标窗口无效"

            left, top, right, bottom = win32gui.GetWindowRect(handle)
            width = right - left
            height = bottom - top
            if width <= 0 or height <= 0:
                return False, "窗口尺寸无效"
            if not (0 <= point.x < width and 0 <= point.y < height):
                return False, f"相对坐标超出窗口范围：({point.x},{point.y}) / {width}x{height}"

            # Vision coordinates are relative to the captured image; convert
            # them to screen coordinates before sending the mouse event.
            screen_x = left + point.x
            screen_y = top + point.y
            win32gui.SetForegroundWindow(handle)
            win32api.SetCursorPos((screen_x, screen_y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            return True, f"鼠标点击完成：窗口相对坐标 ({point.x},{point.y})"
        except Exception as exc:
            return False, f"鼠标点击失败：{exc}"
