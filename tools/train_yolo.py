from __future__ import annotations

import argparse
from pathlib import Path


def auto_device() -> str:
    try:
        import torch  # type: ignore

        return "0" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def main() -> int:
    parser = argparse.ArgumentParser(description="Train MHXY YOLO detector")
    parser.add_argument("--data", default="data/dataset/data.yaml")
    parser.add_argument("--model", default="yolo11n.pt")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--device", default="auto", help="auto / 0 / cpu")
    args = parser.parse_args()

    data = Path(args.data)
    if not data.exists():
        raise SystemExit(f"dataset yaml not found: {data}")
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise SystemExit("ultralytics is not installed; run: python -m pip install -r requirements.txt") from exc

    device = auto_device() if args.device == "auto" else args.device
    print(f"YOLO训练设备: {device}")
    if device == "0":
        try:
            import torch  # type: ignore
            print(f"GPU: {torch.cuda.get_device_name(0)}")
        except Exception:
            pass

    model = YOLO(args.model)
    model.train(data=str(data), epochs=args.epochs, imgsz=args.imgsz, device=device)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
