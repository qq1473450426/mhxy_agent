from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


class AnnotationCanvas(QLabel):
    def __init__(self) -> None:
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(700, 450)
        self._pixmap: Optional[QPixmap] = None
        self._start = None
        self._rect: Optional[QRect] = None

    def set_image(self, path: Path) -> None:
        pix = QPixmap(str(path))
        if pix.isNull():
            self.clear()
            return
        self._pixmap = pix
        self._rect = None
        self._render()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and self._pixmap:
            self._start = event.position().toPoint()
            self._rect = QRect(self._start, self._start)
            self._render()

    def mouseMoveEvent(self, event) -> None:
        if self._start is not None:
            self._rect = QRect(self._start, event.position().toPoint()).normalized()
            self._render()

    def mouseReleaseEvent(self, event) -> None:
        if self._start is not None:
            self._rect = QRect(self._start, event.position().toPoint()).normalized()
            self._start = None
            self._render()

    def box(self) -> Optional[QRect]:
        return self._rect

    def _render(self) -> None:
        if not self._pixmap:
            return
        scaled = self._pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        canvas = QPixmap(self.size())
        canvas.fill(Qt.black)
        painter = QPainter(canvas)
        x = (self.width() - scaled.width()) // 2
        y = (self.height() - scaled.height()) // 2
        painter.drawPixmap(x, y, scaled)
        if self._rect:
            painter.setPen(QPen(Qt.red, 2))
            painter.drawRect(self._rect)
        painter.end()
        self.setPixmap(canvas)


class DatasetPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.root = Path("data/dataset")
        self.root.mkdir(parents=True, exist_ok=True)
        self.image_dir = self.root / "images"
        self.image_dir.mkdir(parents=True, exist_ok=True)
        self.current: Optional[Path] = None

        self.canvas = AnnotationCanvas()
        self.status = QLabel("先采集一张游戏截图")
        self.classes = QComboBox()
        self.classes.addItems(["npc", "player", "button", "dialog", "task_ui"])

        capture = QPushButton("从游戏截图采集")
        capture.clicked.connect(self.capture_latest)
        save = QPushButton("保存标注")
        save.clicked.connect(self.save_label)

        controls = QHBoxLayout()
        controls.addWidget(capture)
        controls.addWidget(self.classes)
        controls.addWidget(save)

        layout = QVBoxLayout(self)
        layout.addLayout(controls)
        layout.addWidget(self.canvas, 1)
        layout.addWidget(self.status)

    def capture_latest(self) -> None:
        source = Path("data/latest_game_capture.png")
        if not source.exists():
            self.status.setText("没有找到 data/latest_game_capture.png，请先在师门页面截图")
            return
        target = self.image_dir / f"sample_{len(list(self.image_dir.glob('*.png'))):05d}.png"
        QImage(str(source)).save(str(target))
        self.current = target
        self.canvas.set_image(target)
        self.status.setText(f"已采集：{target}")

    def save_label(self) -> None:
        if not self.current or not self.canvas.box():
            self.status.setText("请先采集截图并拖出目标框")
            return
        box = self.canvas.box()
        assert box is not None
        pix = QPixmap(str(self.current))
        if pix.isNull() or pix.width() == 0 or pix.height() == 0:
            self.status.setText("图片无效")
            return
        # The canvas preserves aspect ratio; map the displayed box back to image coordinates.
        scale = min(self.canvas.width() / pix.width(), self.canvas.height() / pix.height())
        disp_w, disp_h = pix.width() * scale, pix.height() * scale
        ox = (self.canvas.width() - disp_w) / 2
        oy = (self.canvas.height() - disp_h) / 2
        x1 = max(0, min(pix.width(), int((box.left() - ox) / scale)))
        y1 = max(0, min(pix.height(), int((box.top() - oy) / scale)))
        x2 = max(0, min(pix.width(), int((box.right() - ox) / scale)))
        y2 = max(0, min(pix.height(), int((box.bottom() - oy) / scale)))
        if x2 <= x1 or y2 <= y1:
            self.status.setText("标注框无效")
            return
        cx = ((x1 + x2) / 2) / pix.width()
        cy = ((y1 + y2) / 2) / pix.height()
        w = (x2 - x1) / pix.width()
        h = (y2 - y1) / pix.height()
        label_dir = self.root / "labels"
        label_dir.mkdir(parents=True, exist_ok=True)
        class_id = self.classes.currentIndex()
        label_path = label_dir / f"{self.current.stem}.txt"
        label_path.write_text(f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n", encoding="utf-8")
        self.status.setText(f"已保存 YOLO 标注：{label_path}")
