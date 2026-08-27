from __future__ import annotations

import random
import shutil
from pathlib import Path
from typing import List, Tuple

CLASSES = ["npc", "player", "button", "dialog", "task_ui"]


class DatasetManager:
    def __init__(self, root: Path = Path("data/dataset")) -> None:
        self.root = root
        self.images = root / "images"
        self.labels = root / "labels"
        self.yaml = root / "data.yaml"

    def prepare(self, val_ratio: float = 0.2, seed: int = 42) -> Tuple[int, int]:
        files = sorted(self.images.glob("*.png")) + sorted(self.images.glob("*.jpg"))
        files = [p for p in files if (self.labels / f"{p.stem}.txt").exists()]
        if not files:
            raise ValueError("没有同时存在图片和 YOLO 标注的数据")
        rng = random.Random(seed)
        rng.shuffle(files)
        val_count = max(1, int(len(files) * val_ratio)) if len(files) > 1 else 0
        val = set(files[:val_count])
        for split in ("train", "val"):
            (self.root / "images" / split).mkdir(parents=True, exist_ok=True)
            (self.root / "labels" / split).mkdir(parents=True, exist_ok=True)
        for image in files:
            split = "val" if image in val else "train"
            shutil.copy2(image, self.root / "images" / split / image.name)
            shutil.copy2(self.labels / f"{image.stem}.txt", self.root / "labels" / split / f"{image.stem}.txt")
        self.yaml.write_text(
            "path: .\n"
            "train: images/train\n"
            "val: images/val\n"
            "names:\n" + "".join(f"  {i}: {name}\n" for i, name in enumerate(CLASSES)),
            encoding="utf-8",
        )
        return len(files) - val_count, val_count


def train_model(data: Path, model_name: str = "yolo11n.pt", epochs: int = 50, imgsz: int = 640, device: str = "") -> Path:
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise RuntimeError("未安装 ultralytics，请先执行 python -m pip install -r requirements.txt") from exc
    model = YOLO(model_name)
    kwargs = {"data": str(data), "epochs": epochs, "imgsz": imgsz, "project": "data/runs", "name": "mhxy"}
    if device:
        kwargs["device"] = device
    result = model.train(**kwargs)
    save_dir = Path(getattr(result, "save_dir", "data/runs/mhxy"))
    best = save_dir / "weights" / "best.pt"
    return best
