from __future__ import annotations


def main() -> int:
    try:
        import torch  # type: ignore
    except Exception as exc:
        print(f"PyTorch导入失败: {exc}")
        return 1

    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA编译版本: {torch.version.cuda}")
    print(f"CUDA可用: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"GPU数量: {torch.cuda.device_count()}")
        for index in range(torch.cuda.device_count()):
            print(f"GPU[{index}]: {torch.cuda.get_device_name(index)}")
            print(f"计算能力: {torch.cuda.get_device_capability(index)}")
        print("YOLO目标设备: cuda:0")
        return 0

    print("YOLO目标设备: cpu")
    print("请检查 NVIDIA 驱动、CUDA版 PyTorch 以及当前虚拟环境。")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
