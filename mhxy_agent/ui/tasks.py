from __future__ import annotations

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem


class TasksPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("今日任务")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        layout.addWidget(title)
        table = QTableWidget(0, 5)
        table.setHorizontalHeaderLabels(["优先级", "任务", "预计时间", "期望收益/小时", "稳定性"])
        for row, values in enumerate([
            ("P0", "核心日常", "30 min", "待计算", "A"),
            ("P1", "高收益活动", "60 min", "待计算", "B"),
            ("P2", "补充任务", "30 min", "待计算", "B"),
        ]):
            table.insertRow(row)
            for col, value in enumerate(values):
                table.setItem(row, col, QTableWidgetItem(value))
        table.resizeColumnsToContents()
        layout.addWidget(table)
