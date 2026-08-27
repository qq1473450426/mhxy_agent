"""Windows game-window observation/execution adapter.

This module intentionally provides a conservative, opt-in window integration:
it can discover and capture a named top-level window, but it does not inject
input automatically. Real execution is enabled only after an explicit user
confirmation path is added to the UI.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WindowInfo:
    title: str
    handle: int


class WindowsObserver:
    def __init__(self, title_keyword: str) -> None:
        self.title_keyword = title_keyword

    def find_window(self) -> WindowInfo | None:
        try:
            import win32gui  # type: ignore
        except ImportError:
            return None

        found: list[WindowInfo] = []

        def callback(hwnd: int, _extra: object) -> None:
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd)
            if self.title_keyword.lower() in title.lower():
                found.append(WindowInfo(title=title, handle=hwnd))

        win32gui.EnumWindows(callback, None)
        return found[0] if found else None

    def observe(self) -> dict[str, object]:
        window = self.find_window()
        if window is None:
            return {"connected": False, "message": "未找到匹配游戏窗口"}
        return {
            "connected": True,
            "title": window.title,
            "handle": window.handle,
            "message": "已找到游戏窗口；等待截图/OCR适配器",
        }
