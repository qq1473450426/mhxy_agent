from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int
    y: int


class WindowsInput:
    """Real Windows mouse input. Points are relative to the captured top-level window."""

    def click(self, handle: int, point: Point) -> tuple[bool, str]:
        try:
            import win32gui  # type: ignore
        except ImportError as exc:
            return False, f"缺少 Windows 输入依赖：{exc}"

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
                # Foreground activation can be denied by Windows focus rules;
                # SendInput may still succeed, so do not fail solely here.
                pass

            if not self._send_input_click(screen_x, screen_y):
                return False, f"SendInput 点击失败：({screen_x},{screen_y})"
            return True, f"鼠标点击完成：窗口相对坐标 ({point.x},{point.y})，屏幕坐标 ({screen_x},{screen_y})"
        except Exception as exc:
            return False, f"鼠标点击失败：{exc}"

    @staticmethod
    def _send_input_click(x: int, y: int) -> bool:
        user32 = ctypes.windll.user32
        screen_w = user32.GetSystemMetrics(0)
        screen_h = user32.GetSystemMetrics(1)
        if screen_w <= 1 or screen_h <= 1:
            return False

        # SendInput absolute coordinates use a 0..65535 virtual desktop range.
        abs_x = round(x * 65535 / (screen_w - 1))
        abs_y = round(y * 65535 / (screen_h - 1))

        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [
                ("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
            ]

        class INPUT(ctypes.Structure):
            _fields_ = [
                ("type", wintypes.DWORD),
                ("mi", MOUSEINPUT),
            ]

        inp = INPUT()
        inp.type = 0  # INPUT_MOUSE
        inp.mi.dx = abs_x
        inp.mi.dy = abs_y
        inp.mi.mouseData = 0
        inp.mi.dwFlags = 0x0001 | 0x8000  # MOVE | ABSOLUTE
        inp.mi.time = 0
        inp.mi.dwExtraInfo = ctypes.pointer(wintypes.ULONG(0))

        move_result = user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
        if move_result != 1:
            return False

        down = INPUT()
        down.type = 0
        down.mi.mouseData = 0
        down.mi.dwFlags = 0x0002  # LEFTDOWN
        down.mi.dwExtraInfo = ctypes.pointer(wintypes.ULONG(0))
        up = INPUT()
        up.type = 0
        up.mi.mouseData = 0
        up.mi.dwFlags = 0x0004  # LEFTUP
        up.mi.dwExtraInfo = ctypes.pointer(wintypes.ULONG(0))

        return user32.SendInput(2, ctypes.byref(down), ctypes.sizeof(INPUT)) == 2
