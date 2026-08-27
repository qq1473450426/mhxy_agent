from mhxy_agent.execution.windows import WindowsObserver


def test_windows_observer_is_safe_off_windows():
    observer = WindowsObserver("Dream")
    result = observer.observe()
    assert isinstance(result, dict)
    assert "connected" in result
