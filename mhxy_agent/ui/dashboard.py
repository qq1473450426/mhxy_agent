from __future__ import annotations

from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QGroupBox, QVBoxLayout, QTableWidget, QTableWidgetItem


class DashboardPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("运行总览")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        layout.addWidget(title)

        cards = QGridLayout()
        for index, (name, value) in enumerate([
            ("Agent 状态", "就绪"),
            ("队伍状态", "模拟模式"),
            ("今日净收益", "¥0"),
            ("收益 / 小时", "¥0"),
        ]):
            box = QGroupBox(name)
            box_layout = QVBoxLayout(box)
            label = QLabel(value)
            label.setStyleSheet("font-size: 20px; font-weight: 600;")
            box_layout.addWidget(label)
            cards.addWidget(box, 0, index)
        layout.addLayout(cards)

        table = QTableWidget(0, 4)
        table.setHorizontalHeaderLabels(["账号", "等级", "状态", "当前任务"])
        for row, values in enumerate([
            ("账号1", "109", "在线", "待规划"),
            ("账号2", "109", "在线", "待规划"),
            ("账号3", "109", "在线", "待规划"),
            ("账号4", "109", "在线", "待规划"),
            ("账号5", "109", "在线", "待规划"),
        ]):
            table.insertRow(row)
            for col, value in enumerate(values):
                table.setItem(row, col, QTableWidgetItem(value))
        table.resizeColumnsToContents()
        layout.addWidget(table)
