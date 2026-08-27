from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Point:
    x: int
    y: int


class WindowsInput:
    """Explicitly controlled Windows input adapter.

    This adapter only performs ordinary foreground-window mouse actions. The
    caller must validate the action and explicitly request execution.
    """

    def click(self, handle: int, point: Point) -> tuple[bool, str]:
        try:
            import win32gui  # type: ignore
            import win32api  # type: ignore
            import win32con  # type: ignore
        except ImportError as exc:
            return False, f"缺少 Windows 输入依赖：{exc}"

        try:
            if not win32gui.IsWindow(handle):
                return False, "目标窗口无效"
            win32gui.SetForegroundWindow(handle)
            left, top, right, bottom = win32gui.GetWindowRect(handle)
            if not (left <= point.x < right and top <= point.y < bottom):
                return False, "点击坐标不在目标窗口内"
            win32api.SetCursorPos((point.x, point.y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            return True, "鼠标点击完成"
        except Exception as exc:
            return False, f"鼠标点击失败：{exc}"
