from __future__ import annotations

"""Desktop adapter for the mhxy_harness runtime.

This module keeps the existing harness core out of the GUI layer while exposing
small, synchronous operations suitable for a PySide6 controller.
"""

import importlib
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Optional


class HarnessAdapter:
    def __init__(self, harness_root: str = "") -> None:
        self.harness_root = Path(harness_root).expanduser() if harness_root else None
        self.settings: Optional[dict[str, Any]] = None
        self.runner: Any = None
        self.window_manager: Any = None
        self._loaded = False

    def _prepare_path(self) -> None:
        if self.harness_root is None:
            return
        root = str(self.harness_root.resolve())
        if root not in sys.path:
            sys.path.insert(0, root)

    def load(self, config_path: str = "config.yaml") -> None:
        self._prepare_path()
        config = importlib.import_module("core.config")
        config.load_env()
        self.settings = config.load_config(config_path)
        window = importlib.import_module("automation.window")
        self.window_manager = window.WindowManager()
        runner_mod = importlib.import_module("game_runner")
        self.runner = runner_mod.GameRunner(self.settings, dry_run=False)
        self._loaded = True

    @property
    def loaded(self) -> bool:
        return self._loaded

    def list_windows(self):
        if self.window_manager is None:
            raise RuntimeError("Harness尚未加载")
        return self.window_manager.find_game_windows()

    def bind_account_window(self, window_title: str):
        if self.window_manager is None:
            raise RuntimeError("Harness尚未加载")
        return self.window_manager.bind_account(window_title)

    def refresh_status(self) -> dict[str, Any]:
        if self.runner is None:
            return {"phase": "unloaded", "running": False}
        return self.runner.status()

    def start(self, task: str = "shimen", goal: str = "完成师门任务") -> bool:
        if self.runner is None:
            raise RuntimeError("Harness尚未加载")
        return bool(self.runner.start(task=task, goal=goal, auto=True))

    def stop(self) -> None:
        if self.runner is not None:
            self.runner.stop()

    def optimize(self, episodes: int = 300) -> dict[str, Any]:
        if self.runner is None:
            raise RuntimeError("Harness尚未加载")
        return dict(self.runner.optimize(episodes=episodes))
