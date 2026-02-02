"""Application entrypoint (`python -m app.main`)."""

import sys

from PySide6.QtWidgets import QApplication

try:
    from .presentation.main_window import MainWindow
except ImportError:
    from app.presentation.main_window import MainWindow


def main() -> int:
    """Starts the Qt application.

    Returns:
        Process exit code.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
