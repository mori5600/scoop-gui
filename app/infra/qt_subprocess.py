import subprocess

from PySide6.QtCore import QObject, Signal, Slot


class SubprocessWorker(QObject):
    """Runs a subprocess in a background Qt thread.

    The worker is meant to be moved to a `QThread` and started via a signal/slot.
    """

    finished = Signal(bytes, bytes, int)

    def __init__(self, argv: list[str], timeout_sec: int = 60):
        """Initializes the worker.

        Args:
            argv: Process argv to execute.
            timeout_sec: Maximum time to wait before aborting.
        """
        super().__init__()
        self._argv = argv
        self._timeout_sec = timeout_sec

    @Slot()
    def run(self):
        """Executes the configured command and emits `finished`."""
        try:
            result = subprocess.run(
                self._argv,
                capture_output=True,
                timeout=self._timeout_sec,
            )
            self.finished.emit(result.stdout, result.stderr, result.returncode)
        except subprocess.TimeoutExpired:
            self.finished.emit(b"", b"timeout: command exceeded limit", 124)
        except Exception as e:
            self.finished.emit(b"", str(e).encode("utf-8", errors="replace"), 1)
