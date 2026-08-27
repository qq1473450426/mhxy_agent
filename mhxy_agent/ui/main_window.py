from __future__ import annotations

from PySide6.QtWidgets import QMainWindow, QListWidget, QStackedWidget, QWidget, QHBoxLayout

from .dashboard import DashboardPage
from .strategy import StrategyPage
from .tasks import TasksPage
from .mentor import MentorPage


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MHXY Agent")
        self.resize(1180, 760)
        self.nav = QListWidget()
        self.nav.addItems(["总览", "Strategy Brain", "今日任务", "师门任务"])
        self.nav.setFixedWidth(180)
        self.stack = QStackedWidget()
        self.stack.addWidget(DashboardPage())
        self.stack.addWidget(StrategyPage())
        self.stack.addWidget(TasksPage())
        self.stack.addWidget(MentorPage())
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.addWidget(self.nav)
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(root)
