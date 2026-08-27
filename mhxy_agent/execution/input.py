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
    """Windows mouse input. Points use the same full-window pixel space as WindowCapture."""

    LEFTDOWN = 0x0002
    LEFTUP = 0x0004
    MOUSEEVENTF_MOVE = 0x0001
    MOUSEEVENTF_ABSOLUTE = 0x8000
    MOUSEEVENTF_VIRTUALDESK = 0x4000

    def __init__(self) -> None:
        self._set_dpi_awareness()
        self._user32 = ctypes.windll.user32

    @staticmethod
    def _set_dpi_awareness() -> None:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

    @staticmethod
    def _screen_metrics() -> Tuple[int, int, int, int]:
        user32 = ctypes.windll.user32
        left = int(user32.GetSystemMetrics(76))
        top = int(user32.GetSystemMetrics(77))
        width = int(user32.GetSystemMetrics(78))
        height = int(user32.GetSystemMetrics(79))
        return left, top, width, height

    def _set_cursor_pos(self, x: int, y: int) -> Tuple[bool, str]:
        """Move the real Windows cursor; fall back to SendInput if SetCursorPos fails."""
        try:
            if bool(self._user32.SetCursorPos(int(x), int(y))):
                return True, "SetCursorPos"
        except Exception:
            pass

        try:
            left, top, width, height = self._screen_metrics()
            if width <= 1 or height <= 1:
                return False, "屏幕尺寸无效"
            ax = round((int(x) - left) * 65535 / (width - 1))
            ay = round((int(y) - top) * 65535 / (height - 1))

            class MOUSEINPUT(ctypes.Structure):
                _fields_ = [
                    ("dx", wintypes.LONG),
                    ("dy", wintypes.LONG),
                    ("mouseData", wintypes.DWORD),
                    ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", ctypes.c_void_p),
                ]

            class INPUT(ctypes.Structure):
                _fields_ = [("type", wintypes.DWORD), ("mi", MOUSEINPUT)]

            inp = INPUT(
                type=0,
                mi=MOUSEINPUT(
                    dx=ax,
                    dy=ay,
                    mouseData=0,
                    dwFlags=self.MOUSEEVENTF_MOVE | self.MOUSEEVENTF_ABSOLUTE | self.MOUSEEVENTF_VIRTUALDESK,
                    time=0,
                    dwExtraInfo=None,
                ),
            )
            sent = int(self._user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT)))
            if sent == 1:
                return True, "SendInput"
            return False, f"SendInput返回={sent}"
        except Exception as exc:
            return False, f"SendInput异常={exc}"

    def move_to(self, handle: int, point: Point, duration: float = 0.8) -> Tuple[bool, str]:
        """Move the visible system cursor along a smooth path without clicking."""
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
            ok, method = self._human_move(start, (screen_x, screen_y), duration)
            actual = win32api.GetCursorPos()
            if not ok:
                return False, f"鼠标移动失败：目标屏幕坐标 ({screen_x},{screen_y})，最后光标=({actual[0]},{actual[1]})，方式={method}"
            return True, f"鼠标已移动到：窗口相对 ({point.x},{point.y})，屏幕 ({screen_x},{screen_y})，最终光标=({actual[0]},{actual[1]})，方式={method}"
        except Exception as exc:
            err = ctypes.get_last_error()
            return False, f"鼠标移动失败：目标屏幕坐标 ({screen_x},{screen_y})，Win32Error={err}，异常={exc}"

    def _send_button(self, flag: int) -> Tuple[bool, str]:
        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [
                ("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_void_p),
            ]

        class INPUT(ctypes.Structure):
            _fields_ = [("type", wintypes.DWORD), ("mi", MOUSEINPUT)]

        inp = INPUT(
            type=0,
            mi=MOUSEINPUT(dx=0, dy=0, mouseData=0, dwFlags=flag, time=0, dwExtraInfo=None),
        )
        sent = int(self._user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT)))
        return (sent == 1, f"SendInput鼠标按键返回={sent}")

    def click(self, handle: int, point: Point, move_duration: float = 0.8, settle_delay: float = 0.15) -> Tuple[bool, str]:
        """Move the visible cursor to the target, pause, then issue a left click."""
        ok, message = self.move_to(handle, point, duration=move_duration)
        if not ok:
            return False, message
        time.sleep(max(0.0, settle_delay))
        down_ok, down_msg = self._send_button(self.LEFTDOWN)
        time.sleep(0.07)
        up_ok, up_msg = self._send_button(self.LEFTUP)
        if down_ok and up_ok:
            return True, message + f"；已执行左键点击，停留={settle_delay:.2f}s；{down_msg}；{up_msg}"
        return False, message + f"；鼠标按键发送失败；{down_msg}；{up_msg}"

    def _human_move(self, start: Tuple[int, int], end: Tuple[int, int], duration: float) -> Tuple[bool, str]:
        """Move the real cursor along a visible curved path."""
        sx, sy = start
        ex, ey = end
        distance = math.hypot(ex - sx, ey - sy)
        if distance < 1:
            return True, "already_at_target"

        duration = max(0.25, min(1.5, duration * (0.9 + min(distance / 800.0, 0.6))))
        steps = max(18, min(90, int(distance / 8)))
        nx = -(ey - sy) / distance
        ny = (ex - sx) / distance
        curve = min(16.0, max(2.0, distance * 0.025))
        curve *= 1.0 if random.random() >= 0.5 else -1.0
        cx = (sx + ex) / 2.0 + nx * curve
        cy = (sy + ey) / 2.0 + ny * curve
        method = ""

        for i in range(1, steps + 1):
            t = i / steps
            u = t * t * (3.0 - 2.0 * t)
            one = 1.0 - u
            x = one * one * sx + 2 * one * u * cx + u * u * ex
            y = one * one * sy + 2 * one * u * cy + u * u * ey
            ok, method = self._set_cursor_pos(round(x), round(y))
            if not ok:
                return False, method
            time.sleep(duration / steps)

        ok, method = self._set_cursor_pos(ex, ey)
        return ok, method
