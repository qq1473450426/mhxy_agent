from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWidget

from ..config import AppConfig
from ..execution.game_session import GameSession
from ..execution.mentor_detector import MentorTargetDetector
from ..execution.vision_fusion import VisionFusion
from ..execution.visual_debug import render_debug


class MentorPage(QWidget):
    """Real-window mentor workflow with explicit click-target visualization."""

    def __init__(self) -> None:
        super().__init__()
        self.session = GameSession(AppConfig.from_env().game_window_keyword)
        self.fusion = VisionFusion()
        self.detector = MentorTargetDetector()
        self.last_action = None
        self.last_image = None
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("师门任务 · YOLO + OCR 视觉模式"))

        row = QHBoxLayout()
        row.addWidget(QLabel("游戏窗口："))
        self.window_box = QComboBox()
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
        self.step = QPushButton("执行识别动作")
        self.step.clicked.connect(self.execute_one)
        self.step.setEnabled(False)
        stop = QPushButton("停止")
        stop.clicked.connect(self.stop)
        buttons.addWidget(observe)
        buttons.addWidget(self.step)
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

    def _show_preview(self, path: Path) -> None:
        self.preview.setPixmap(QPixmap(str(path)).scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def _render_target(self, click_point: Optional[tuple[int, int]], result: Optional[bool] = None) -> None:
        if self.last_image is None:
            return
        path = render_debug(
            self.last_image,
            (),
            (),
            output="data/latest_click_target.png" if result is None else "data/latest_click_result.png",
            click_point=click_point,
            click_result=result,
        )
        self._show_preview(path)

    def refresh_windows(self) -> None:
        windows = self.session.observer.list_windows()
        self.window_box.clear()
        for window in windows:
            self.window_box.addItem(window.title, window.handle)
        self.output.append(f"发现 {len(windows)} 个可见窗口")

    def connect_selected(self) -> None:
        handle = self.window_box.currentData()
        if handle is None:
            self.output.append("请先刷新并选择游戏窗口。")
            return
        window = self.session.observer.find_by_handle(int(handle))
        if window is None:
            self.status.setText("状态：未连接")
            self.output.append("所选窗口已不存在，请刷新窗口列表。")
            return
        self.session.window = window
        self.last_action = None
        self.step.setEnabled(False)
        self.status.setText("状态：已连接")
        self.output.append(f"已连接：{window.title} (HWND={window.handle})")

    def observe_real(self) -> None:
        if self.session.window is None:
            self.connect_selected()
        if self.session.window is None:
            return
        result = self.session.snapshot()
        if not result.ok or result.image is None:
            self.output.append(result.message)
            self.status.setText("状态：截图失败")
            return
        image = result.image
        self.last_image = image
        path = Path("data/latest_game_capture.png")
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path)

        fused = self.fusion.analyze(image)
        self.last_action = self.detector.detect(fused.ocr, image)
        debug_path = render_debug(image, fused.yolo, fused.ocr.regions)
        self._show_preview(debug_path)

        self.output.append(f"截图成功：{image.size[0]}x{image.size[1]}")
        self.output.append(f"OCR：{fused.ocr.text or '未识别到文字'}")
        self.output.append(f"OCR区域：{len(fused.ocr.regions)}")
        self.output.append(f"YOLO检测：{len(fused.yolo)}")
        if fused.yolo:
            for target in fused.targets:
                self.output.append(f"YOLO：{target.label} {target.confidence:.0%} box={target.box} OCR={target.ocr_text or '-'}")
        elif self.fusion.detector.error:
            self.output.append(f"YOLO：{self.fusion.detector.error}")
        else:
            self.output.append("YOLO：当前画面未检测到目标")

        if self.last_action is None:
            self.step.setEnabled(False)
            self.output.append("未找到师门任务红色链接，不执行点击。")
            self.status.setText("状态：已截图，未找到目标")
        else:
            self.step.setEnabled(True)
            self.output.append(f"候选目标：{self.last_action.target}；窗口相对坐标：{self.last_action.point}")
            self.output.append("绿色十字 = 准备点击位置；确认前绝不移动鼠标。")
            self._render_target(self.last_action.point)
            self.status.setText("状态：已识别，请检查绿色点击标记")

    def execute_one(self) -> None:
        if self.last_action is None or self.last_action.point is None:
            self.observe_real()
        if self.last_action is None or self.last_action.point is None:
            return
        point = self.last_action.point
        self._render_target(point)
        answer = QMessageBox.question(
            self,
            "确认执行",
            f"识别目标：{self.last_action.target}\n窗口相对坐标：{point}\n\n绿色十字就是准备点击的位置。\n请确认它落在右侧任务面板红色“师父”文字上。\n\n确认后才会真实点击一次。",
        )
        if answer != QMessageBox.Yes:
            self.output.append("用户取消执行；未发送鼠标输入。")
            return
        ok, message = self.session.click(point[0], point[1])
        self.output.append(message)
        self._render_target(point, ok)
        self.output.append("预览标记：CLICK OK=已发送输入；CLICK FAILED=输入失败。")
        self.status.setText("状态：已执行一次" if ok else "状态：执行失败")
        self.last_action = None
        self.step.setEnabled(False)

    def stop(self) -> None:
        self.last_action = None
        self.step.setEnabled(False)
        self.output.append("执行已停止。")
        self.status.setText("状态：已停止")
