from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass


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
                pass

            if not self._send_input_click(screen_x, screen_y):
                err = ctypes.get_last_error()
                return False, f"SendInput 点击失败：屏幕坐标 ({screen_x},{screen_y})，Win32Error={err}"
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

        abs_x = round(x * 65535 / (screen_w - 1))
        abs_y = round(y * 65535 / (screen_h - 1))
        ULONG_PTR = ctypes.c_size_t

        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [
                ("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ULONG_PTR),
            ]

        class INPUT_UNION(ctypes.Union):
            _fields_ = [("mi", MOUSEINPUT)]

        class INPUT(ctypes.Structure):
            _anonymous_ = ("u",)
            _fields_ = [
                ("type", wintypes.DWORD),
                ("u", INPUT_UNION),
            ]

        def make_input(dx: int, dy: int, flags: int) -> INPUT:
            item = INPUT()
            item.type = 0  # INPUT_MOUSE
            item.mi.dx = dx
            item.mi.dy = dy
            item.mi.mouseData = 0
            item.mi.dwFlags = flags
            item.mi.time = 0
            item.mi.dwExtraInfo = 0
            return item

        move = make_input(abs_x, abs_y, 0x0001 | 0x8000)  # MOVE | ABSOLUTE
        if user32.SendInput(1, ctypes.byref(move), ctypes.sizeof(INPUT)) != 1:
            return False

        down = make_input(0, 0, 0x0002)  # LEFTDOWN
        up = make_input(0, 0, 0x0004)  # LEFTUP
        inputs = (INPUT * 2)(down, up)
        return user32.SendInput(2, inputs, ctypes.sizeof(INPUT)) == 2
