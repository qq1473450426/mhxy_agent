from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Point:
    x: int
    y: int


class WindowsInput:
    """Windows mouse input via pywin32.

    Coordinates are relative to the selected game window. Movement is visible
    and verified after every move so coordinate/input failures are explicit.
    """

    def __init__(self) -> None:
        try:
            import win32api  # type: ignore
            import win32con  # type: ignore
            import win32gui  # type: ignore
        except ImportError as exc:
            raise RuntimeError(f"缺少 pywin32：{exc}") from exc
        self.win32api = win32api
        self.win32con = win32con
        self.win32gui = win32gui

    def _screen_point(self, handle: int, point: Point) -> Tuple[bool, str, int, int]:
        if not self.win32gui.IsWindow(handle):
            return False, "目标窗口无效", 0, 0
        left, top, right, bottom = self.win32gui.GetWindowRect(handle)
        width, height = right - left, bottom - top
        if width <= 0 or height <= 0:
            return False, "窗口尺寸无效", 0, 0
        if not (0 <= point.x < width and 0 <= point.y < height):
            return False, f"相对坐标超出窗口范围：({point.x},{point.y}) / {width}x{height}", 0, 0
        return True, "", left + point.x, top + point.y

    def _move_cursor(self, x: int, y: int) -> None:
        # pywin32 exposes SetCursorPos as a single tuple argument. There is no
        # win32api.MoveTo API; the previous implementation therefore failed
        # before a single mouse movement was attempted.
        self.win32api.SetCursorPos((int(x), int(y)))

    def move_to(self, handle: int, point: Point, duration: float = 0.45) -> Tuple[bool, str]:
        ok, msg, sx, sy = self._screen_point(handle, point)
        if not ok:
            return False, msg
        try:
            self.win32gui.SetForegroundWindow(handle)
        except Exception:
            pass
        try:
            start = self.win32api.GetCursorPos()
            distance = math.hypot(sx - start[0], sy - start[1])
            if distance < 2:
                self._move_cursor(sx, sy)
            else:
                duration = max(0.18, min(0.8, duration))
                steps = max(12, min(50, int(distance / 14)))
                nx = -(sy - start[1]) / distance
                ny = (sx - start[0]) / distance
                curve = random.uniform(-10.0, 10.0)
                cx = (start[0] + sx) / 2.0 + nx * curve
                cy = (start[1] + sy) / 2.0 + ny * curve
                for i in range(1, steps + 1):
                    t = i / steps
                    u = t * t * (3.0 - 2.0 * t)
                    one = 1.0 - u
                    px = one * one * start[0] + 2 * one * u * cx + u * u * sx
                    py = one * one * start[1] + 2 * one * u * cy + u * u * sy
                    self._move_cursor(round(px), round(py))
                    time.sleep(duration / steps)
                self._move_cursor(sx, sy)
            actual = self.win32api.GetCursorPos()
            if abs(actual[0] - sx) <= 3 and abs(actual[1] - sy) <= 3:
                return True, f"鼠标移动完成：窗口({point.x},{point.y}) → 屏幕({sx},{sy}) → 实际({actual[0]},{actual[1]})，方式=pywin32.SetCursorPos"
            return False, f"鼠标移动后坐标异常：目标({sx},{sy})，实际({actual[0]},{actual[1]})"
        except Exception as exc:
            return False, f"pywin32鼠标移动失败：目标屏幕({sx},{sy})，异常={exc}"

    def click(self, handle: int, point: Point, move_duration: float = 0.45, settle_delay: float = 0.12) -> Tuple[bool, str]:
        ok, message = self.move_to(handle, point, duration=move_duration)
        if not ok:
            return False, message
        try:
            time.sleep(max(0.0, settle_delay))
            self.win32api.mouse_event(self.win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.06)
            self.win32api.mouse_event(self.win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            return True, message + f"；pywin32左键完成，停留={settle_delay:.2f}s"
        except Exception as exc:
            return False, f"pywin32鼠标点击失败：{exc}"
