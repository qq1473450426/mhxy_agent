from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget
)

from ..config import AppConfig
from ..execution.game_session import GameSession
from ..execution.service import ExecutionService


class MentorPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.service = ExecutionService()
        self.session = GameSession(AppConfig.from_env().game_window_keyword)

        layout = QVBoxLayout(self)
        title = QLabel("师门任务 · Windows 单步模式")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        layout.addWidget(title)

        row = QHBoxLayout()
        row.addWidget(QLabel("窗口关键词："))
        self.keyword = QComboBox()
        self.keyword.setEditable(True)
        self.keyword.addItems([AppConfig.from_env().game_window_keyword, "梦幻西游", "网易梦幻西游"])
        row.addWidget(self.keyword, 1)
        connect = QPushButton("连接游戏")
        connect.clicked.connect(self.connect_game)
        row.addWidget(connect)
        layout.addLayout(row)

        buttons = QHBoxLayout()
        observe = QPushButton("真实截图")
        observe.clicked.connect(self.observe_real)
        step = QPushButton("模拟执行一步")
        step.clicked.connect(self.step_simulation)
        stop = QPushButton("停止")
        stop.clicked.connect(lambda: self.status.setText("执行状态：已停止"))
        buttons.addWidget(observe)
        buttons.addWidget(step)
        buttons.addWidget(stop)
        layout.addLayout(buttons)

        self.status = QLabel("状态：未连接")
        layout.addWidget(self.status)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

    def connect_game(self) -> None:
        self.session = GameSession(self.keyword.currentText().strip() or "梦幻西游")
        ok, message = self.session.connect()
        self.status.setText(f"状态：{'已连接' if ok else '未连接'}")
        self.output.append(message)

    def observe_real(self) -> None:
        if self.session.window is None:
            self.output.append("请先点击【连接游戏】")
            return
        result = self.session.snapshot()
        if hasattr(result, "ok"):
            self.output.append(f"截图：{'成功' if result.ok else '失败'} | {result.message}")
        else:
            self.output.append("截图接口未返回有效结果")

    def step_simulation(self) -> None:
        result = self.service.step()
        self.output.append(f"Simulation Action/Verify: {result}")
        self.status.setText(f"执行状态：{'成功' if result['success'] else '失败/拦截'}")
