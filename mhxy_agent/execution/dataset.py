from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple


@dataclass(frozen=True)
class YoloBox:
    class_id: int
    x1: float
    y1: float
    x2: float
    y2: float

    def to_line(self, width: int, height: int) -> str:
        cx = ((self.x1 + self.x2) / 2.0) / width
        cy = ((self.y1 + self.y2) / 2.0) / height
        bw = abs(self.x2 - self.x1) / width
        bh = abs(self.y2 - self.y1) / height
        values = (self.class_id, cx, cy, bw, bh)
        return " ".join(str(v) for v in values)


class YoloDataset:
    """Small dependency-free YOLO dataset writer for captured game frames."""

    def __init__(self, root: str = "data/dataset") -> None:
        self.root = Path(root)
        self.train_images = self.root / "images" / "train"
        self.val_images = self.root / "images" / "val"
        self.train_labels = self.root / "labels" / "train"
        self.val_labels = self.root / "labels" / "val"
        for directory in (self.train_images, self.val_images, self.train_labels, self.val_labels):
            directory.mkdir(parents=True, exist_ok=True)

    def add_label_file(self, split: str, stem: str, width: int, height: int, boxes: Iterable[YoloBox]) -> Path:
        if split not in ("train", "val"):
            raise ValueError("split must be train or val")
        target = self.train_labels if split == "train" else self.val_labels
        path = target / f"{stem}.txt"
        lines = [box.to_line(width, height) for box in boxes]
        path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        return path

    def write_data_yaml(self, names: Iterable[str]) -> Path:
        names_list: List[str] = list(names)
        path = self.root / "data.yaml"
        lines = [
            f"path: {self.root.resolve().as_posix()}",
            "train: images/train",
            "val: images/val",
            f"nc: {len(names_list)}",
            "names:",
        ]
        lines.extend(f"  {i}: {name}" for i, name in enumerate(names_list))
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path
