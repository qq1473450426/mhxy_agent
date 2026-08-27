from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWidget

from ..config import AppConfig
from ..execution.game_session import GameSession
from ..execution.mentor_detector import MentorTargetDetector
from ..execution.vision import VisionEngine


class MentorPage(QWidget):
    """Real-window mentor workflow: observe -> detect -> explicit click."""

    def __init__(self) -> None:
        super().__init__()
        self.session = GameSession(AppConfig.from_env().game_window_keyword)
        self.vision = VisionEngine()
        self.detector = MentorTargetDetector()
        self.last_action = None

        layout = QVBoxLayout(self)
        title = QLabel("师门任务 · 真实窗口单步模式")
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
        observe = QPushButton("截图 / 识别")
        observe.clicked.connect(self.observe_real)
        step = QPushButton("执行识别动作")
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
        self.session = GameSession(self.keyword.currentText().strip())
        ok, message = self.session.connect()
        self.status.setText("状态：已连接" if ok else "状态：未连接")
        self.output.append(message)

    def observe_real(self) -> None:
        if self.session.window is None:
            self.connect_game()
        if self.session.window is None:
            return
        result = self.session.snapshot()
        if not hasattr(result, "ok") or not result.ok:
            self.output.append(getattr(result, "message", "截图失败"))
            return
        image = result.image
        if image is None:
            return
        image.save("data/latest_game_capture.png")
        pixmap = QPixmap("data/latest_game_capture.png")
        self.preview.setPixmap(pixmap.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        vision = self.vision.analyze(image)
        self.last_action = self.detector.detect(vision)
        self.output.append(f"OCR：{vision.text or '未识别到文字'}")
        if self.last_action is None:
            self.output.append("未找到师门目标，不执行点击。")
        else:
            self.output.append(f"目标：{self.last_action.target}；坐标：{self.last_action.point}")

    def execute_one(self) -> None:
        if self.last_action is None or self.last_action.point is None:
            self.observe_real()
        if self.last_action is None or self.last_action.point is None:
            return
        point = self.last_action.point
        answer = QMessageBox.question(self, "确认执行", f"识别目标：{self.last_action.target}\n坐标：{point}\n\n确认点击一次？")
        if answer != QMessageBox.Yes:
            self.output.append("用户取消执行。")
            return
        ok, message = self.session.click(point[0], point[1])
        self.output.append(message)
        self.status.setText("状态：已执行一次" if ok else "状态：执行失败")
        self.last_action = None

    def stop(self) -> None:
        self.last_action = None
        self.output.append("执行已停止。")
        self.status.setText("状态：已停止")
