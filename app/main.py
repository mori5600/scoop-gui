"""Application entrypoint (`python -m app.main`)."""

import sys

from PySide6.QtWidgets import QApplication

from app.logging import init_logger
from app.presentation.main_window import MainWindow


def main() -> int:
    logger = init_logger()
    try:
        logger.info("Starting application")
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        return app.exec()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0
    except Exception:
        logger.exception("Application error")
        return 1
    finally:
        logger.info("Application stopped")
        logger.complete()


if __name__ == "__main__":
    raise SystemExit(main())
