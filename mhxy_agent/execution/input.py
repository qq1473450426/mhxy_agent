from __future__ import annotations

import ctypes
import time
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Point:
    x: int
    y: int


class WindowsInput:
    """Visible desktop mouse input. PyAutoGUI is primary; user32 is fallback."""

    def __init__(self) -> None:
        self._pyautogui = None
        try:
            import pyautogui  # type: ignore
            pyautogui.FAILSAFE = False
            pyautogui.PAUSE = 0.02
            self._pyautogui = pyautogui
        except Exception:
            pass

    def _screen_point(self, handle: int, point: Point) -> Tuple[bool, str, int, int]:
        try:
            import win32gui  # type: ignore
            if not win32gui.IsWindow(handle):
                return False, "目标窗口无效", 0, 0
            left, top, right, bottom = win32gui.GetWindowRect(handle)
            width, height = right - left, bottom - top
            if width <= 0 or height <= 0:
                return False, "窗口尺寸无效", 0, 0
            if not (0 <= point.x < width and 0 <= point.y < height):
                return False, f"相对坐标超出窗口范围：({point.x},{point.y}) / {width}x{height}", 0, 0
            return True, "", left + point.x, top + point.y
        except Exception as exc:
            return False, f"获取窗口坐标失败：{exc}", 0, 0

    def move_to(self, handle: int, point: Point, duration: float = 0.65) -> Tuple[bool, str]:
        ok, msg, sx, sy = self._screen_point(handle, point)
        if not ok:
            return False, msg
        try:
            import win32gui  # type: ignore
            win32gui.SetForegroundWindow(handle)
        except Exception:
            pass

        if self._pyautogui is not None:
            try:
                self._pyautogui.moveTo(sx, sy, duration=max(0.2, min(1.2, duration)), tween=self._pyautogui.easeInOutQuad)
                actual = self._pyautogui.position()
                if abs(actual.x - sx) <= 3 and abs(actual.y - sy) <= 3:
                    return True, f"鼠标移动完成：窗口({point.x},{point.y}) → 屏幕({sx},{sy}) → 实际({actual.x},{actual.y})，方式=PyAutoGUI"
            except Exception:
                pass

        try:
            if bool(ctypes.windll.user32.SetCursorPos(int(sx), int(sy))):
                return True, f"鼠标移动完成：窗口({point.x},{point.y}) → 屏幕({sx},{sy})，方式=user32"
        except Exception:
            pass
        return False, f"鼠标移动失败：目标屏幕({sx},{sy})，PyAutoGUI和user32均失败"

    def click(self, handle: int, point: Point, move_duration: float = 0.65, settle_delay: float = 0.15) -> Tuple[bool, str]:
        ok, message = self.move_to(handle, point, duration=move_duration)
        if not ok:
            return False, message
        time.sleep(max(0.0, settle_delay))
        if self._pyautogui is not None:
            try:
                self._pyautogui.click(button="left")
                return True, message + f"；PyAutoGUI左键完成，停留={settle_delay:.2f}s"
            except Exception:
                pass
        try:
            user32 = ctypes.windll.user32
            user32.mouse_event(0x0002, 0, 0, 0, 0)
            time.sleep(0.07)
            user32.mouse_event(0x0004, 0, 0, 0, 0)
            return True, message + "；user32左键完成"
        except Exception as exc:
            return False, f"鼠标点击失败：{exc}"
