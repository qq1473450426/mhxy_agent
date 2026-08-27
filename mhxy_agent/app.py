"""PySide6 desktop application for MHXY Agent."""
from __future__ import annotations

import sys
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QApplication, QMainWindow

from .models import GameProfile
from .strategy import StrategyEngine
from .ui.main_window import MainWindow


class AgentWorker(QObject):
    finished = Signal()
    message = Signal(str)

    @Slot()
    def run(self) -> None:
        try:
            profile = GameProfile.example()
            plan = StrategyEngine().create_daily_plan(profile, hours=2)
            self.message.emit(f"策略计算完成：{len(plan)} 个任务")
            for i, task in enumerate(plan, 1):
                self.message.emit(f"{i}. [{task.priority}] {task.name} | {task.expected_profit:.0f}/小时")
        except Exception as exc:
            self.message.emit(f"执行失败：{type(exc).__name__}: {exc}")
        finally:
            self.finished.emit()


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
