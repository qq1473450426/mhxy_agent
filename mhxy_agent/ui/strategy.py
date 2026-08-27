from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit


class StrategyPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Strategy Brain")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        layout.addWidget(title)
        layout.addWidget(QLabel("当前决策链：Game Profile → Economy → Strategy → Task Planner → Safety → Executor"))
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlainText("等待策略引擎运行…\n\n当前模式：Simulation\n执行器：MockExecutor\n安全模式：启用")
        layout.addWidget(self.output)
