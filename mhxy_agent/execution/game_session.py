from __future__ import annotations

from typing import Optional

from .windows import WindowsObserver, WindowInfo
from .capture import WindowCapture
from .input import Point, WindowsInput


class GameSession:
    """Coordinates window discovery, capture, and explicit input."""

    def __init__(self, title_keyword: str) -> None:
        self.observer = WindowsObserver(title_keyword)
        self.capture = WindowCapture()
        self.input = WindowsInput()
        self.window: Optional[WindowInfo] = None

    def connect(self) -> tuple[bool, str]:
        self.window = self.observer.find_window()
        if self.window is None:
            return False, "未找到游戏窗口，请先启动游戏并检查窗口标题关键词"
        return True, f"已连接：{self.window.title} (HWND={self.window.handle})"

    def snapshot(self):
        if self.window is None:
            return self.capture.__class__.__name__, None
        return self.capture.capture(self.window.handle)

    def click(self, x: int, y: int) -> tuple[bool, str]:
        if self.window is None:
            return False, "尚未连接游戏窗口"
        return self.input.click(self.window.handle, Point(x, y))
