from __future__ import annotations

from pathlib import Path
from time import perf_counter
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QCheckBox, QComboBox, QHBoxLayout, QLabel, QMessageBox, QPushButton, QTextEdit, QVBoxLayout, QWidget

from ..config import AppConfig
from ..execution.dialogue import DialogueDetector
from ..execution.game_session import GameSession
from ..execution.mentor_detector import MentorTargetDetector
from ..execution.task_panel import TaskPanelOCR
from ..execution.vision_fusion import VisionFusion
from ..execution.visual_debug import render_debug


class MentorPage(QWidget):
    """Real-window mentor workflow with OCR-first observation."""

    def __init__(self) -> None:
        super().__init__()
        self.session = GameSession(AppConfig.from_env().game_window_keyword)
        self.fusion = VisionFusion()
        self.task_ocr = TaskPanelOCR()
        self.dialogue = DialogueDetector()
        self.detector = MentorTargetDetector()
        self.last_action = None
        self.last_dialogue = None
        self.last_image = None
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("师门任务 · OCR快速模式 / YOLO可选"))

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
        self.yolo_check = QCheckBox("启用YOLO（较慢）")
        self.yolo_check.setChecked(False)
        self.move_test = QPushButton("移动到目标（不点击）")
        self.move_test.clicked.connect(self.move_to_target)
        self.move_test.setEnabled(False)
        self.step = QPushButton("执行识别动作")
        self.step.clicked.connect(self.execute_one)
        self.step.setEnabled(False)
        self.dialogue_step = QPushButton("识别对话 / 师门任务")
        self.dialogue_step.clicked.connect(self.detect_dialogue)
        self.dialogue_step.setEnabled(False)
        stop = QPushButton("停止")
        stop.clicked.connect(self.stop)
        buttons.addWidget(observe)
        buttons.addWidget(self.yolo_check)
        buttons.addWidget(self.move_test)
        buttons.addWidget(self.step)
        buttons.addWidget(self.dialogue_step)
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
            self.last_image, (), (),
            output="data/latest_click_target.png" if result is None else "data/latest_click_result.png",
            click_point=click_point, click_result=result,
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
        self.last_dialogue = None
        self.step.setEnabled(False)
        self.move_test.setEnabled(False)
        self.dialogue_step.setEnabled(False)
        self.status.setText("状态：已连接")
        self.output.append(f"已连接：{window.title} (HWND={window.handle})")

    def observe_real(self) -> None:
        if self.session.window is None:
            self.connect_selected()
        if self.session.window is None:
            return
        t0 = perf_counter()
        result = self.session.snapshot()
        capture_ms = (perf_counter() - t0) * 1000
        if not result.ok or result.image is None:
            self.output.append(result.message)
            self.status.setText("状态：截图失败")
            return
        image = result.image
        self.last_image = image
        path = Path("data/latest_game_capture.png")
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path)

        t1 = perf_counter()
        task_ocr = self.task_ocr.analyze(image)
        ocr_ms = (perf_counter() - t1) * 1000
        t2 = perf_counter()
        use_yolo = self.yolo_check.isChecked()
        fused = self.fusion.analyze(image, use_yolo=use_yolo, ocr_result=task_ocr)
        yolo_ms = (perf_counter() - t2) * 1000 if use_yolo else 0.0
        self.last_action = self.detector.detect(task_ocr, image)
        debug_path = render_debug(image, fused.yolo, task_ocr.regions)
        self._show_preview(debug_path)

        self.output.append(f"截图成功：{image.size[0]}x{image.size[1]}；截图耗时={capture_ms:.0f}ms")
        self.output.append(f"任务面板 OCR ROI：x≥{int(image.size[0] * self.task_ocr.x_ratio)}，y≥{int(image.size[1] * self.task_ocr.y_ratio)}")
        self.output.append(f"任务面板 OCR：{task_ocr.text or '未识别到文字'}；OCR耗时={ocr_ms:.0f}ms")
        self.output.append(f"OCR区域：{len(task_ocr.regions)}")
        if use_yolo:
            self.output.append(f"YOLO检测：{len(fused.yolo)}；YOLO耗时={yolo_ms:.0f}ms；设备={self.fusion.detector.device_name}")
            for target in fused.targets:
                self.output.append(f"YOLO：{target.label} {target.confidence:.0%} box={target.box} OCR={target.ocr_text or '-'}")
            if not fused.yolo and self.fusion.detector.error:
                self.output.append(f"YOLO：{self.fusion.detector.error}")
        else:
            self.output.append("YOLO：未启用，本次未运行模型")

        if self.last_action is None:
            self.step.setEnabled(False)
            self.move_test.setEnabled(False)
            self.dialogue_step.setEnabled(True)
            self.output.append("未找到师门任务红色链接；可尝试‘识别对话 / 师门任务’检测当前对话框。")
            self.status.setText("状态：已截图，未找到任务链接")
        else:
            self.step.setEnabled(True)
            self.move_test.setEnabled(True)
            self.dialogue_step.setEnabled(False)
            self.output.append(f"候选目标：{self.last_action.target}；窗口相对坐标：{self.last_action.point}")
            self.output.append("绿色十字 = 准备点击位置；确认前绝不移动鼠标。")
            self._render_target(self.last_action.point)
            self.status.setText("状态：已识别，请先用‘移动到目标’检查坐标")

    def detect_dialogue(self) -> None:
        if self.session.window is None:
            self.connect_selected()
        if self.session.window is None:
            return
        t0 = perf_counter()
        result = self.session.snapshot()
        capture_ms = (perf_counter() - t0) * 1000
        if not result.ok or result.image is None:
            self.output.append(result.message)
            self.status.setText("状态：截图失败")
            return
        image = result.image
        self.last_image = image
        t1 = perf_counter()
        dialogue_result = self.dialogue.analyze(image)
        ocr_ms = (perf_counter() - t1) * 1000
        self.output.append(f"对话框截图：{image.size[0]}x{image.size[1]}；截图耗时={capture_ms:.0f}ms")
        self.output.append(f"对话框 OCR：{dialogue_result.text or '未识别到文字'}；OCR耗时={ocr_ms:.0f}ms")
        self.output.append(f"对话框 OCR区域：{len(dialogue_result.regions)}")
        option = self.dialogue.find_option(dialogue_result, "师门任务")
        self.last_dialogue = option
        if option is None:
            self.output.append("未找到‘师门任务’选项，不执行点击。")
            self.status.setText("状态：对话已识别，未找到师门任务")
            return
        self.output.append(f"对话选项：{option.text}；窗口相对坐标：{option.point}；置信度={option.confidence:.0%}")
        self.output.append("绿色十字 = 对话选项准备点击位置。")
        self._render_target(option.point)
        self.status.setText("状态：已找到‘师门任务’，可移动检查")
        self.move_test.setEnabled(True)
        self.step.setEnabled(True)

    def move_to_target(self) -> None:
        point = None
        target_name = ""
        if self.last_dialogue is not None:
            point = self.last_dialogue.point
            target_name = self.last_dialogue.text
        elif self.last_action is not None:
            point = self.last_action.point
            target_name = self.last_action.target
        if point is None:
            return
        self._render_target(point)
        self.output.append(f"开始可见鼠标移动：{target_name}；窗口相对坐标 {point}；本次仅移动，不点击。")
        ok, message = self.session.move_cursor(point[0], point[1], duration=0.45)
        self.output.append(message)
        self.status.setText("状态：鼠标已到目标位置（未点击）" if ok else "状态：鼠标移动失败")

    def execute_one(self) -> None:
        point = None
        target_name = ""
        if self.last_dialogue is not None:
            point = self.last_dialogue.point
            target_name = self.last_dialogue.text
        elif self.last_action is not None:
            point = self.last_action.point
            target_name = self.last_action.target
        if point is None:
            return
        self._render_target(point)
        answer = QMessageBox.question(
            self, "确认执行",
            f"识别目标：{target_name}\n窗口相对坐标：{point}\n\n鼠标会沿可见轨迹移动到绿色十字后左键点击。\n请确认它位于正确的游戏选项上。",
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
        self.last_dialogue = None
        self.step.setEnabled(False)
        self.move_test.setEnabled(False)
        if ok:
            self.dialogue_step.setEnabled(True)
            self.output.append("下一步：重新截图/识别当前对话；可继续识别‘师门任务’选项或后续对话。")

    def stop(self) -> None:
        self.last_action = None
        self.last_dialogue = None
        self.step.setEnabled(False)
        self.move_test.setEnabled(False)
        self.dialogue_step.setEnabled(False)
        self.output.append("执行已停止。")
        self.status.setText("状态：已停止")
