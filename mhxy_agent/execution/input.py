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

    def click(
        self,
        handle: int,
        point: Point,
        move_duration: float = 0.45,
        settle_delay: float = 0.12,
    ) -> Tuple[bool, str]:
        """Move the visible system cursor to the target, pause, then click.

        The cursor is moved in small visible steps instead of teleporting with
        absolute SendInput coordinates. This makes coordinate debugging possible
        and avoids capture/absolute-coordinate scaling mismatches.
        """
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

            screen_x = left + point.x
            screen_y = top + point.y
            try:
                win32gui.SetForegroundWindow(handle)
            except Exception:
                pass

            start = win32api.GetCursorPos()
            self._human_move(win32api, start, (screen_x, screen_y), move_duration)
            time.sleep(max(0.0, settle_delay))

            # The cursor is already visibly positioned at the target. Press/release there.
            win32api.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
            time.sleep(0.055)
            win32api.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP

            actual = win32api.GetCursorPos()
            return True, (
                f"鼠标点击完成：窗口相对坐标 ({point.x},{point.y})，"
                f"屏幕坐标 ({screen_x},{screen_y})，移动=可见轨迹，"
                f"耗时≈{move_duration:.2f}s，最终光标=({actual[0]},{actual[1]})"
            )
        except Exception as exc:
            err = ctypes.get_last_error()
            return False, f"鼠标点击失败：目标屏幕坐标 ({screen_x},{screen_y})，Win32Error={err}，异常={exc}"

    @staticmethod
    def _human_move(win32api: object, start: Tuple[int, int], end: Tuple[int, int], duration: float) -> None:
        """Move the real cursor along a smooth, slightly curved human-visible path."""
        sx, sy = start
        ex, ey = end
        distance = math.hypot(ex - sx, ey - sy)
        if distance < 1:
            return

        duration = max(0.18, min(0.9, duration * (0.75 + min(distance / 800.0, 0.75))))
        steps = max(12, min(60, int(distance / 12)))

        nx = -(ey - sy) / distance
        ny = (ex - sx) / distance
        curve = min(18.0, max(3.0, distance * 0.035))
        curve *= 1.0 if random.random() >= 0.5 else -1.0
        cx = (sx + ex) / 2.0 + nx * curve
        cy = (sy + ey) / 2.0 + ny * curve

        for i in range(1, steps + 1):
            t = i / steps
            u = t * t * (3.0 - 2.0 * t)  # smoothstep timing
            one = 1.0 - u
            x = one * one * sx + 2 * one * u * cx + u * u * ex
            y = one * one * sy + 2 * one * u * cy + u * u * ey
            win32api.SetCursorPos((round(x), round(y)))
            time.sleep(duration / steps)

        win32api.SetCursorPos((ex, ey))
