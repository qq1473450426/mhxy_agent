from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..config import AppConfig
from ..execution.game_session import GameSession
from ..execution.mentor import MentorPlanner


class MentorPage(QWidget):
    """Real-window observation page with explicit single-step controls."""

    def __init__(self) -> None:
        super().__init__()
        self.session = GameSession(AppConfig.from_env().game_window_keyword)
        self.planner = MentorPlanner()
        self._last_image = None

        layout = QVBoxLayout(self)
        title = QLabel("师门任务 · Windows 单步模式")
        title.setStyleSheet("font-size: 22px; font-weight: 700;")
        layout.addWidget(title)

        row = QHBoxLayout()
        row.addWidget(QLabel("窗口关键词："))
        self.keyword = QComboBox()
        self.keyword.setEditable(True)
        self.keyword.addItem(AppConfig.from_env().game_window_keyword)
        row.addWidget(self.keyword, 1)
        connect = QPushButton("连接游戏")
        connect.clicked.connect(self.connect_game)
        row.addWidget(connect)
        layout.addLayout(row)

        self.status = QLabel("状态：未连接")
        layout.addWidget(self.status)

        buttons = QHBoxLayout()
        observe = QPushButton("截图 / 观察")
        observe.clicked.connect(self.observe_real)
        step = QPushButton("执行一步")
        step.clicked.connect(self.execute_one)
        stop = QPushButton("停止")
        stop.clicked.connect(self.stop)
        buttons.addWidget(observe)
        buttons.addWidget(step)
        buttons.addWidget(stop)
        layout.addLayout(buttons)

        self.preview = QLabel("暂无截图")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumHeight(260)
        self.preview.setStyleSheet("border: 1px solid #888;")
        layout.addWidget(self.preview)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output, 1)

    def connect_game(self) -> None:
        keyword = self.keyword.currentText().strip()
        self.session = GameSession(keyword)
        ok, message = self.session.connect()
        self.status.setText(f"状态：{'已连接' if ok else '未连接'}")
        self.output.append(message)

    def observe_real(self) -> None:
        if self.session.window is None:
            self.connect_game()
            if self.session.window is None:
                return
        result = self.session.snapshot()
        if hasattr(result, "ok"):
            if not result.ok:
                self.output.append(result.message)
                return
            self._last_image = result.image
            if result.image is not None:
                image = result.image
                image.save("data/latest_game_capture.png")
                pixmap = QPixmap("data/latest_game_capture.png")
                self.preview.setPixmap(pixmap.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.output.append(f"真实截图：{result.message}")

    def execute_one(self) -> None:
        self.output.append("单步执行尚未绑定游戏坐标：请先完成视觉识别后再执行。")

    def stop(self) -> None:
        self.output.append("执行已停止。")
        self.status.setText("状态：已停止")
