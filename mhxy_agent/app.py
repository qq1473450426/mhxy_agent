"""PySide6 desktop application for MHXY Agent."""
from __future__ import annotations

import sys
from pathlib import Path
from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout

from .models import GameProfile
from .strategy import StrategyEngine


class AgentWorker(QObject):
    finished = Signal()
    message = Signal(str)

    @Slot()
    def run(self) -> None:
        try:
            profile = GameProfile.example()
            engine = StrategyEngine()
            plan = engine.create_daily_plan(profile, hours=2)
            self.message.emit(f"策略计算完成：{len(plan)} 个任务")
            for i, task in enumerate(plan, 1):
                self.message.emit(f"{i}. [{task.priority}] {task.name} | {task.expected_profit:.0f}/小时")
        except Exception as exc:
            self.message.emit(f"执行失败：{exc}")
        finally:
            self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MHXY Agent")
        self.resize(1100, 720)
        self.thread: QThread | None = None
        self.worker: AgentWorker | None = None

        root = QWidget()
        layout = QVBoxLayout(root)
        title = QLabel("MHXY Agent · Strategy Brain")
        title.setStyleSheet("font-size: 24px; font-weight: 700;")
        layout.addWidget(title)

        status = QLabel("状态：就绪 | Python + PySide6")
        layout.addWidget(status)

        buttons = QHBoxLayout()
        start = QPushButton("▶ 运行策略模拟")
        start.clicked.connect(self.start_agent)
        stop = QPushButton("■ 停止")
        stop.clicked.connect(self.stop_agent)
        buttons.addWidget(start)
        buttons.addWidget(stop)
        layout.addLayout(buttons)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        self.setCentralWidget(root)

    def start_agent(self) -> None:
        if self.thread and self.thread.isRunning():
            return
        self.thread = QThread(self)
        self.worker = AgentWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.message.connect(self.log.append)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()
        self.log.append("Agent：开始运行策略模拟…")

    def stop_agent(self) -> None:
        if self.thread and self.thread.isRunning():
            self.thread.requestInterruption()
            self.thread.quit()
            self.log.append("Agent：已请求停止。")


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
