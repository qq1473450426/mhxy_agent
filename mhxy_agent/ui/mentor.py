from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QHBoxLayout

from ..execution.service import ExecutionService


class MentorPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.service = ExecutionService()
        layout = QVBoxLayout(self)
        title = QLabel("师门任务 · 单步安全模式")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        layout.addWidget(title)

        self.status = QLabel("执行器：MockExecutor | 模式：Simulation")
        layout.addWidget(self.status)

        buttons = QHBoxLayout()
        observe = QPushButton("截图/观察")
        observe.clicked.connect(self.observe)
        step = QPushButton("执行一步")
        step.clicked.connect(self.step)
        stop = QPushButton("停止")
        stop.clicked.connect(lambda: self.status.setText("执行状态：已停止"))
        buttons.addWidget(observe)
        buttons.addWidget(step)
        buttons.addWidget(stop)
        layout.addLayout(buttons)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)
        self._timer = QTimer(self)
        self._timer.timeout.connect(lambda: None)

    def observe(self) -> None:
        obs = self.service.executor.observe()
        self.output.append(f"Observation: {obs}")

    def step(self) -> None:
        result = self.service.step()
        self.output.append(f"Action/Verify: {result}")
        self.status.setText(f"执行状态：{'成功' if result['success'] else '已拦截/失败'}")
