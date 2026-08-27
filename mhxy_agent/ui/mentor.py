from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWidget

from ..config import AppConfig
from ..execution.game_session import GameSession
from ..execution.mentor_detector import MentorTargetDetector
from ..execution.vision import VisionEngine


class MentorPage(QWidget):
    """Real-window mentor workflow: select -> observe -> detect -> explicit click."""

    def __init__(self) -> None:
        super().__init__()
        self.session = GameSession(AppConfig.from_env().game_window_keyword)
        self.vision = VisionEngine()
        self.detector = MentorTargetDetector()
        self.last_action = None
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("师门任务 · 真实窗口单步模式"))

        row = QHBoxLayout()
        row.addWidget(QLabel("游戏窗口："))
        self.window_box = QComboBox()
        self.window_box.setEditable(True)
        row.addWidget(self.window_box, 1)
        refresh = QPushButton("刷新窗口")
        refresh.clicked.connect(self.refresh_windows)
        row.addWidget(refresh)
        connect = QPushButton("连接所选窗口")
        connect.clicked.connect(self.connect_selected)
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
        self.refresh_windows()

    def refresh_windows(self) -> None:
        windows = self.session.observer.list_windows()
        self.window_box.clear()
        for window in windows:
            self.window_box.addItem(window.title, window.handle)
        self.output.append(f"发现 {len(windows)} 个可见窗口")

    def connect_selected(self) -> None:
        handle = self.window_box.currentData()
        title = self.window_box.currentText().strip()
        if handle is not None:
            window = self.session.observer.find_by_handle(int(handle))
            if window is None:
                ok, message = False, "所选窗口已不存在，请刷新窗口列表"
            else:
                self.session.window = window
                ok, message = True, f"已连接：{window.title} (HWND={window.handle})"
        elif title:
            self.session = GameSession(title)
            ok, message = self.session.connect()
        else:
            ok, message = False, "请先刷新并选择窗口"
        self.status.setText("状态：已连接" if ok else "状态：未连接")
        self.output.append(message)

    def observe_real(self) -> None:
        if self.session.window is None:
            self.connect_selected()
        if self.session.window is None:
            return
        result = self.session.snapshot()
        if not getattr(result, "ok", False):
            self.output.append(getattr(result, "message", "截图失败"))
            return
        image = result.image
        if image is None:
            self.output.append("截图为空")
            return
        image.save("data/latest_game_capture.png")
        self.preview.setPixmap(QPixmap("data/latest_game_capture.png").scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        vision = self.vision.analyze(image)
        self.last_action = self.detector.detect(vision)
        self.output.append(f"OCR：{vision.text or '未识别到文字'}")
        self.output.append("未找到师门目标，不执行点击。" if self.last_action is None else f"目标：{self.last_action.target}；坐标：{self.last_action.point}")

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
