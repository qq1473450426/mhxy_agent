from __future__ import annotations

import ctypes
import math
import random
import time
from ctypes import wintypes
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Point:
    x: int
    y: int


class WindowsInput:
    """Windows mouse input. Points are in the same pixel space as WindowCapture."""

    def __init__(self) -> None:
        self._set_dpi_awareness()

    @staticmethod
    def _set_dpi_awareness() -> None:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

    def move_to(self, handle: int, point: Point, duration: float = 0.8) -> Tuple[bool, str]:
        """Move the real visible cursor to a window-relative point without clicking."""
        try:
            import win32gui  # type: ignore
            import win32api  # type: ignore
        except ImportError as exc:
            return False, f"缺少 Windows 输入依赖：{exc}"

        screen_x = screen_y = 0
        try:
            if not win32gui.IsWindow(handle):
                return False, "目标窗口无效"
            left, top, right, bottom = win32gui.GetWindowRect(handle)
            width, height = right - left, bottom - top
            if width <= 0 or height <= 0:
                return False, "窗口尺寸无效"
            if not (0 <= point.x < width and 0 <= point.y < height):
                return False, f"相对坐标超出窗口范围：({point.x},{point.y}) / {width}x{height}"
            screen_x, screen_y = left + point.x, top + point.y
            try:
                win32gui.SetForegroundWindow(handle)
            except Exception:
                pass
            start = win32api.GetCursorPos()
            self._human_move(win32api, start, (screen_x, screen_y), duration)
            actual = win32api.GetCursorPos()
            return True, f"鼠标已移动到：窗口相对 ({point.x},{point.y})，屏幕 ({screen_x},{screen_y})，最终光标=({actual[0]},{actual[1]})"
        except Exception as exc:
            err = ctypes.get_last_error()
            return False, f"鼠标移动失败：目标屏幕坐标 ({screen_x},{screen_y})，Win32Error={err}，异常={exc}"

    def click(self, handle: int, point: Point, move_duration: float = 0.8, settle_delay: float = 0.15) -> Tuple[bool, str]:
        """Move the visible system cursor to the target, pause, then click."""
        ok, message = self.move_to(handle, point, duration=move_duration)
        if not ok:
            return False, message
        try:
            import win32api  # type: ignore
            time.sleep(max(0.0, settle_delay))
            win32api.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
            time.sleep(0.07)
            win32api.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
            return True, message + f"；已执行左键点击，停留={settle_delay:.2f}s"
        except Exception as exc:
            err = ctypes.get_last_error()
            return False, f"鼠标点击失败：已移动到目标但按键发送失败，Win32Error={err}，异常={exc}"

    @staticmethod
    def _human_move(win32api: object, start: Tuple[int, int], end: Tuple[int, int], duration: float) -> None:
        """Move the real cursor along a smooth, visible path for debugging."""
        sx, sy = start
        ex, ey = end
        distance = math.hypot(ex - sx, ey - sy)
        if distance < 1:
            return

        duration = max(0.25, min(1.5, duration * (0.9 + min(distance / 800.0, 0.6))))
        steps = max(18, min(90, int(distance / 8)))
        nx = -(ey - sy) / distance
        ny = (ex - sx) / distance
        curve = min(16.0, max(2.0, distance * 0.025))
        curve *= 1.0 if random.random() >= 0.5 else -1.0
        cx = (sx + ex) / 2.0 + nx * curve
        cy = (sy + ey) / 2.0 + ny * curve

        for i in range(1, steps + 1):
            t = i / steps
            u = t * t * (3.0 - 2.0 * t)
            one = 1.0 - u
            x = one * one * sx + 2 * one * u * cx + u * u * ex
            y = one * one * sy + 2 * one * u * cy + u * u * ey
            win32api.SetCursorPos((round(x), round(y)))
            time.sleep(duration / steps)
        win32api.SetCursorPos((ex, ey))
