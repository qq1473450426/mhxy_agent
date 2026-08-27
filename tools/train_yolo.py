from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Train MHXY YOLO detector")
    parser.add_argument("--data", default="data/dataset/data.yaml")
    parser.add_argument("--model", default="yolo11n.pt")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="")
    args = parser.parse_args()

    data = Path(args.data)
    if not data.exists():
        raise SystemExit(f"dataset yaml not found: {data}")
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise SystemExit("ultralytics is not installed; run: python -m pip install -r requirements.txt") from exc

    model = YOLO(args.model)
    kwargs = {"data": str(data), "epochs": args.epochs, "imgsz": args.imgsz}
    if args.device:
        kwargs["device"] = args.device
    model.train(**kwargs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
