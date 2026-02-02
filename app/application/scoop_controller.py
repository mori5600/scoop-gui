from PySide6.QtCore import QObject, QThread, Signal

from app.core.scoop_export_parser import parse_scoop_export
from app.infra.powershell import build_powershell_argv
from app.infra.qt_subprocess import SubprocessWorker


class ScoopController(QObject):
    """Orchestrates Scoop commands and exposes results via Qt signals."""

    log = Signal(str)
    error = Signal(str)
    loaded = Signal(object)  # list[ScoopApp]

    def __init__(self, parent: QObject | None = None):
        """Initializes the controller.

        Args:
            parent: Optional Qt parent object.
        """
        super().__init__(parent)
        self._thread: QThread | None = None
        self._worker: SubprocessWorker | None = None
        self._active_job_id = 0

    def refresh_installed_apps(self) -> None:
        """Loads installed apps via `scoop export` in the background."""
        if self._thread is not None:
            self.log.emit("[info] already running")
            return

        self._active_job_id += 1
        job_id = self._active_job_id

        self.log.emit("$ scoop export")
        self.log.emit("[running] ...")

        cmd = "$ErrorActionPreference='Stop'; scoop export 6> $null; exit $LASTEXITCODE"
        argv = build_powershell_argv(cmd)

        thread = QThread()
        worker = SubprocessWorker(argv=argv, timeout_sec=60)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)

        worker.finished.connect(
            lambda stdout, stderr, returncode, jid=job_id: self._on_finished(
                jid, stdout, stderr, returncode
            )
        )
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(lambda t=thread: self._on_thread_finished(t))

        self._thread = thread
        self._worker = worker
        thread.start()

    def _on_thread_finished(self, finished_thread: QThread) -> None:
        """Clears references only if the finished thread is still the active one.

        Args:
            finished_thread: The thread that has emitted `finished`.
        """
        if self._thread is finished_thread:
            self._thread = None
            self._worker = None

    @staticmethod
    def _decode(data: bytes) -> str:
        """Decodes process output bytes with a small encoding fallback list.

        Args:
            data: Raw bytes to decode.

        Returns:
            Decoded text.
        """
        for enc in ("utf-8", "cp932"):
            try:
                return data.decode(enc)
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="replace")

    def _on_finished(
        self, job_id: int, stdout: bytes, stderr: bytes, returncode: int
    ) -> None:
        """Handles a finished Scoop job.

        Args:
            job_id: Monotonic identifier used to ignore stale results.
            stdout: Raw stdout bytes.
            stderr: Raw stderr bytes.
            returncode: Process return code.
        """
        if job_id != self._active_job_id:
            return

        out = self._decode(stdout)
        err = self._decode(stderr)

        if err.strip():
            self.log.emit(err.rstrip())

        if returncode != 0:
            self.error.emit(f"[error] scoop failed (code={returncode})")
            return

        apps = parse_scoop_export(out)
        if apps is None:
            self.error.emit("[error] failed to parse scoop export json")
            return

        self.loaded.emit(apps)
        self.log.emit(f"[loaded] {len(apps)} packages")
