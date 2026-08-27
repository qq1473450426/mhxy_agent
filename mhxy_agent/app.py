"""PySide6 desktop application entry point.

Supports both recommended package execution and direct ``python app.py``
execution from the repository root.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

try:
    # Normal: python -m mhxy_agent
    from .ui.main_window import MainWindow
except ImportError:
    # Direct execution: python mhxy_agent/app.py
    package_root = Path(__file__).resolve().parent.parent
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))
    from mhxy_agent.ui.main_window import MainWindow


def main() -> int:
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
