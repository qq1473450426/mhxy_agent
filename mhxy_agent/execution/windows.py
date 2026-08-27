"""Windows game-window discovery adapter."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class WindowInfo:
    title: str
    handle: int


class WindowsObserver:
    def __init__(self, title_keyword: str = "") -> None:
        self.title_keyword = title_keyword.strip()
        self.last_error = ""

    def list_windows(self) -> List[WindowInfo]:
        self.last_error = ""
        try:
            import win32gui  # type: ignore
        except ImportError as exc:
            self.last_error = f"未安装 pywin32：{exc}"
            return []

        found: List[WindowInfo] = []

        def callback(hwnd: int, _extra: object) -> None:
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd).strip()
            if title:
                found.append(WindowInfo(title=title, handle=hwnd))

        try:
            win32gui.EnumWindows(callback, None)
        except Exception as exc:
            self.last_error = f"枚举 Windows 窗口失败：{exc}"
        return found

    def find_window(self) -> Optional[WindowInfo]:
        windows = self.list_windows()
        if self.title_keyword:
            key = self.title_keyword.casefold()
            matches = [w for w in windows if key in w.title.casefold()]
            if matches:
                return matches[0]
        return None

    def find_by_handle(self, handle: int) -> Optional[WindowInfo]:
        for window in self.list_windows():
            if window.handle == handle:
                return window
        return None

    def observe(self) -> dict:
        windows = self.list_windows()
        window = self.find_window()
        if window is None:
            message = self.last_error or "未找到匹配窗口；请刷新窗口列表并选择实际游戏窗口标题"
            return {
                "connected": False,
                "message": message,
                "windows": [w.title for w in windows],
            }
        return {"connected": True, "title": window.title, "handle": window.handle}
