from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QComboBox, QFormLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox,
    QPushButton, QSpinBox, QTextEdit, QVBoxLayout, QWidget,
)

from ..harness_adapter import HarnessAdapter


class HarnessPage(QWidget):
    """PySide6 control surface for mhxy_harness without a web backend."""

    def __init__(self) -> None:
        super().__init__()
        self.adapter = HarnessAdapter()
        self.window_box = QComboBox()
        self.task_box = QComboBox()
        self.task_box.addItem("师门", "shimen")
        self.task_box.addItem("抓鬼", "ghost")
        self.task_box.addItem("封妖", "yao")
        self.goal = QLineEdit("完成师门任务")
        self.episodes = QSpinBox()
        self.episodes.setRange(1, 100000)
        self.episodes.setValue(300)
        self.status = QLabel("Harness：未加载")
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh_status)

        root = QVBoxLayout(self)
        root.addWidget(QLabel("MHXY Harness · PySide6 本地控制台"))

        form = QFormLayout()
        root_path = QLineEdit(str(Path.cwd() / "mhxy_harness"))
        load = QPushButton("加载 Harness")
        load.clicked.connect(lambda: self.load_harness(root_path.text()))
        path_row = QHBoxLayout()
        path_row.addWidget(root_path, 1)
        path_row.addWidget(load)
        form.addRow("Harness目录", path_row)

        window_row = QHBoxLayout()
        window_row.addWidget(self.window_box, 1)
        refresh = QPushButton("刷新游戏窗口")
        refresh.clicked.connect(self.refresh_windows)
        bind = QPushButton("绑定当前窗口")
        bind.clicked.connect(self.bind_window)
        window_row.addWidget(refresh)
        window_row.addWidget(bind)
        form.addRow("游戏窗口", window_row)
        form.addRow("任务", self.task_box)
        form.addRow("目标", self.goal)
        form.addRow("RL训练轮数", self.episodes)
        root.addLayout(form)

        buttons = QHBoxLayout()
        start = QPushButton("启动真实任务")
        start.clicked.connect(self.start_real)
        stop = QPushButton("停止")
        stop.clicked.connect(self.stop_real)
        optimize = QPushButton("训练优化")
        optimize.clicked.connect(self.optimize)
        buttons.addWidget(start)
        buttons.addWidget(stop)
        buttons.addWidget(optimize)
        root.addLayout(buttons)
        root.addWidget(self.status)
        root.addWidget(self.output, 1)
        self.load_harness(str(Path.cwd() / "mhxy_harness"))

    def load_harness(self, path: str) -> None:
        try:
            self.adapter = HarnessAdapter(path)
            self.adapter.load(str(Path(path) / "config.yaml"))
            self.status.setText("Harness：已加载")
            self.output.append(f"Harness加载成功：{path}")
            self.refresh_windows()
            self._timer.start(1000)
        except Exception as exc:
            self.status.setText("Harness：加载失败")
            self.output.append(f"Harness加载失败：{exc}")

    def refresh_windows(self) -> None:
        if not self.adapter.loaded:
            return
        try:
            wins = self.adapter.list_windows()
            self.window_box.clear()
            for win in wins:
                self.window_box.addItem(win.title, win.hwnd)
            self.output.append(f"发现游戏窗口：{len(wins)}")
        except Exception as exc:
            self.output.append(f"刷新窗口失败：{exc}")

    def bind_window(self) -> None:
        idx = self.window_box.currentIndex()
        if idx < 0:
            self.output.append("没有可绑定的游戏窗口")
            return
        title = self.window_box.currentText()
        try:
            win = self.adapter.bind_account_window(title)
            self.output.append(f"已绑定：HWND={win.hwnd} rect={win.rect}")
        except Exception as exc:
            self.output.append(f"绑定失败：{exc}")

    def start_real(self) -> None:
        if not self.adapter.loaded:
            return
        self.bind_window()
        task = str(self.task_box.currentData() or "shimen")
        try:
            ok = self.adapter.start(task=task, goal=self.goal.text().strip() or "完成任务")
            self.output.append(f"真实任务启动：{'成功' if ok else '失败'}，task={task}")
        except Exception as exc:
            QMessageBox.critical(self, "启动失败", str(exc))

    def stop_real(self) -> None:
        try:
            self.adapter.stop()
            self.output.append("已发送停止命令")
        except Exception as exc:
            self.output.append(f"停止失败：{exc}")

    def optimize(self) -> None:
        try:
            result = self.adapter.optimize(self.episodes.value())
            self.output.append(f"优化结果：{result}")
        except Exception as exc:
            self.output.append(f"优化失败：{exc}")

    def refresh_status(self) -> None:
        try:
            status = self.adapter.refresh_status()
            self.status.setText(f"Harness：phase={status.get('phase')} running={status.get('running')}")
        except Exception as exc:
            self.status.setText(f"状态错误：{exc}")
