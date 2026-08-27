from mhxy_agent.execution.capture import WindowCapture
from mhxy_agent.execution.vision import VisionEngine


def test_capture_handles_missing_windows_dependencies():
    result = WindowCapture().capture(0)
    assert isinstance(result.ok, bool)
    assert isinstance(result.message, str)


def test_vision_engine_is_deterministic_without_ocr():
    result = VisionEngine().analyze(object())
    assert result.scene == "unknown"
    assert result.confidence == 0.0
