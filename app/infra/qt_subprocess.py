import os
import subprocess
from typing import Final

from logly import logger
from PySide6.QtCore import QObject, Signal, Slot

_CREATE_NO_WINDOW: Final[int] = 0x08000000


class SubprocessWorker(QObject):
    """Runs a subprocess in a background Qt thread.

    The worker is meant to be moved to a `QThread` and started via a signal/slot.
    """

    finished = Signal(bytes, bytes, int)

    def __init__(self, argv: list[str], timeout_sec: int = 60):
        super().__init__()
        self._argv = argv
        self._timeout_sec = timeout_sec

    @Slot()
    def run(self):
        """Executes the configured command and emits `finished`."""
        try:
            logger.info(
                f"Starting subprocess timeout={self._timeout_sec}s argv={' '.join(self._argv)}"
            )
            kwargs: dict = {
                "capture_output": True,
                "timeout": self._timeout_sec,
            }

            if os.name == "nt":
                kwargs["creationflags"] = _CREATE_NO_WINDOW

            result = subprocess.run(self._argv, **kwargs)
            logger.info(f"Subprocess finished returncode={result.returncode}")
            self.finished.emit(result.stdout, result.stderr, result.returncode)

        except subprocess.TimeoutExpired:
            logger.warning("Subprocess timed out")
            self.finished.emit(b"", b"timeout: command exceeded limit", 124)
        except Exception as e:
            logger.exception("Subprocess execution failed")
            self.finished.emit(b"", str(e).encode("utf-8", errors="replace"), 1)
