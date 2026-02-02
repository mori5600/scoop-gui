from typing import Callable

from PySide6.QtCore import QObject, QThread, Signal, QTimer

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
        self._refresh_after_finish = False

    def refresh_installed_apps(self) -> None:
        """Loads installed apps via `scoop export` in the background."""
        self._start_job(
            label="scoop export",
            command="scoop export 6> $null",
            on_finished=self._on_export_finished,
            timeout_sec=60,
        )

    def update_app(self, name: str) -> None:
        """Updates the specified app via `scoop update`."""
        quoted = self._ps_quote(name)
        self._run_scoop_command(
            label=f"scoop update {name}",
            command=f"scoop update {quoted}",
            refresh_after=True,
            timeout_sec=600,
        )

    def uninstall_app(self, name: str) -> None:
        """Uninstalls the specified app via `scoop uninstall`."""
        quoted = self._ps_quote(name)
        self._run_scoop_command(
            label=f"scoop uninstall {name}",
            command=f"scoop uninstall {quoted}",
            refresh_after=True,
            timeout_sec=300,
        )

    def cleanup_all(self) -> None:
        """Cleans old versions for all apps via `scoop cleanup`."""
        self._run_scoop_command(
            label="scoop cleanup --all",
            command="scoop cleanup --all",
            refresh_after=True,
            timeout_sec=600,
        )

    def _on_thread_finished(self, finished_thread: QThread) -> None:
        """Clears references only if the finished thread is still the active one.

        Args:
            finished_thread: The thread that has emitted `finished`.
        """
        if self._thread is finished_thread:
            self._thread = None
            self._worker = None
            if self._refresh_after_finish:
                self._refresh_after_finish = False
                QTimer.singleShot(0, self.refresh_installed_apps)

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

    def _emit_output(self, text: str) -> None:
        """Emits non-empty output to the log signal."""
        output = text.rstrip()
        if output:
            self.log.emit(output)

    def _start_job(
        self,
        label: str,
        command: str,
        on_finished: Callable[[int, bytes, bytes, int], None],
        timeout_sec: int,
    ) -> None:
        if self._thread is not None:
            self.log.emit("[info] already running")
            return

        self._active_job_id += 1
        job_id = self._active_job_id
        self._refresh_after_finish = False

        self.log.emit(f"$ {label}")
        self.log.emit("[running] ...")

        cmd = f"$ErrorActionPreference='Stop'; {command}; exit $LASTEXITCODE"
        argv = build_powershell_argv(cmd)

        thread = QThread()
        worker = SubprocessWorker(argv=argv, timeout_sec=timeout_sec)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)

        worker.finished.connect(
            lambda stdout, stderr, returncode, jid=job_id: on_finished(
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

    def _run_scoop_command(
        self,
        label: str,
        command: str,
        refresh_after: bool,
        timeout_sec: int,
    ) -> None:
        self._start_job(
            label=label,
            command=command,
            on_finished=lambda jid, stdout, stderr, returncode, ra=refresh_after: (
                self._on_command_finished(jid, stdout, stderr, returncode, ra)
            ),
            timeout_sec=timeout_sec,
        )

    @staticmethod
    def _ps_quote(value: str) -> str:
        """Quotes a value for PowerShell single-quoted literals."""
        return "'" + value.replace("'", "''") + "'"

    def _on_export_finished(
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

    def _on_command_finished(
        self,
        job_id: int,
        stdout: bytes,
        stderr: bytes,
        returncode: int,
        refresh_after: bool,
    ) -> None:
        """Handles finished Scoop commands that are not `scoop export`."""
        if job_id != self._active_job_id:
            return

        out = self._decode(stdout)
        err = self._decode(stderr)

        self._emit_output(out)
        self._emit_output(err)

        if returncode != 0:
            self.error.emit(f"[error] scoop failed (code={returncode})")
            return

        if refresh_after:
            self._refresh_after_finish = True
