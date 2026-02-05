import re
from typing import Callable

from PySide6.QtCore import QObject, QThread, Signal

from app.core.scoop_export_parser import parse_scoop_export
from app.core.scoop_search_parser import parse_scoop_search
from app.infra.powershell import build_powershell_argv
from app.infra.qt_subprocess import SubprocessWorker


class ScoopController(QObject):
    """Orchestrates Scoop commands and exposes results via Qt signals."""

    log = Signal(str)
    error = Signal(str)
    loaded = Signal(object)  # list[ScoopApp]
    searched = Signal(object)  # list[ScoopSearchResult]
    busy_changed = Signal(bool)
    job_started = Signal(str)
    job_finished = Signal(str, int)  # label, returncode

    # Strip common ANSI escape sequences (colors, cursor moves, etc.) so the GUI
    # log doesn't show mojibake like "[33m...".
    _ANSI_OSC_RE = re.compile(r"\x1b\][^\x07]*(?:\x07|\x1b\\)")
    _ANSI_CSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
    _ANSI_2CHAR_RE = re.compile(r"\x1b[@-Z\\-_]")

    def __init__(self, parent: QObject | None = None):
        """Initializes the controller.

        Args:
            parent: Optional Qt parent object.
        """
        super().__init__(parent)
        self._thread: QThread | None = None
        self._worker: SubprocessWorker | None = None
        self._active_job_id = 0
        self._active_label = ""
        self._refresh_after_finish = False

    def is_busy(self) -> bool:
        return self._thread is not None

    def refresh_installed_apps(self) -> None:
        """Loads installed apps via `scoop export` in the background."""
        self._start_job(
            label="scoop export",
            command="scoop export 6> $null",
            on_finished=self._on_export_finished,
            timeout_sec=60,
        )

    def search_apps(self, query: str) -> None:
        """Searches available apps via `scoop search`."""
        q = query.strip()
        if not q:
            self.searched.emit([])
            return

        quoted = self._ps_quote(q)
        # `scoop search` emits PowerShell objects and relies on default formatting.
        # Under some hosts/versions the formatted table isn't captured reliably, so we
        # convert to a compact JSON payload explicitly for stable parsing.
        command = (
            f"$items = @(scoop search {quoted} | ForEach-Object {{ "
            '[pscustomobject]@{ Name = "$($_.Name)"; Version = "$($_.Version)"; '
            'Source = "$($_.Source)"; Binaries = "$($_.Binaries)" } '
            "}); "
            "$items | ConvertTo-Json -Compress"
        )
        self._start_job(
            label=f"scoop search {q}",
            command=command,
            on_finished=self._on_search_finished,
            timeout_sec=60,
            announce=True,
        )

    def install_app(self, name: str) -> None:
        """Installs the specified app via `scoop install`."""
        quoted = self._ps_quote(name)
        self._run_scoop_command(
            label=f"scoop install {name}",
            command=f"scoop install {quoted}",
            refresh_after=True,
            timeout_sec=900,
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

    def update_all_apps(self) -> None:
        """Updates all installed apps via `scoop update --all`."""
        self._run_scoop_command(
            label="scoop update --all",
            command="scoop update --all",
            refresh_after=True,
            timeout_sec=3600,
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

    def cleanup_app(self, name: str) -> None:
        """Cleans old versions for the specified app via `scoop cleanup`."""
        quoted = self._ps_quote(name)
        self._run_scoop_command(
            label=f"scoop cleanup {name}",
            command=f"scoop cleanup {quoted}",
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
                # Chain refresh without dropping the busy state in-between. This prevents
                # other jobs (e.g. search) from stealing the slot and skipping refresh.
                self.refresh_installed_apps()
                return
            self.busy_changed.emit(False)

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

    @classmethod
    def _sanitize_output(cls, text: str) -> str:
        """Normalizes newlines and removes ANSI escape sequences."""
        if not text:
            return ""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = cls._ANSI_OSC_RE.sub("", text)
        text = cls._ANSI_CSI_RE.sub("", text)
        text = cls._ANSI_2CHAR_RE.sub("", text)
        return text

    def _emit_output(self, text: str) -> None:
        """Emits non-empty output to the log signal."""
        output = self._sanitize_output(text).rstrip()
        if output:
            self.log.emit(output)

    def _start_job(
        self,
        label: str,
        command: str,
        on_finished: Callable[[int, bytes, bytes, int], None],
        timeout_sec: int,
        announce: bool = True,
    ) -> None:
        if self._thread is not None:
            self.log.emit("[info] already running")
            return

        self._active_job_id += 1
        job_id = self._active_job_id
        self._active_label = label
        self._refresh_after_finish = False

        if announce:
            self.log.emit(f"$ {label}")
            self.log.emit("[running] ...")

        self.job_started.emit(label)
        self.busy_changed.emit(True)

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

        err_clean = self._sanitize_output(err)
        if err_clean.strip():
            self.log.emit(err_clean.rstrip())

        if returncode != 0:
            self.error.emit(f"[error] scoop failed (code={returncode})")
            self.job_finished.emit(self._active_label, returncode)
            return

        apps = parse_scoop_export(out)
        if apps is None:
            self.error.emit("[error] failed to parse scoop export json")
            self.job_finished.emit(self._active_label, 1)
            return

        self.loaded.emit(apps)
        self.log.emit(f"[loaded] {len(apps)} packages")
        self.job_finished.emit(self._active_label, 0)

    def _on_search_finished(
        self, job_id: int, stdout: bytes, stderr: bytes, returncode: int
    ) -> None:
        if job_id != self._active_job_id:
            return

        out = self._decode(stdout)
        err = self._decode(stderr)

        combined_clean = self._sanitize_output(out + "\n" + err).strip()
        if combined_clean:
            # Avoid logging the JSON payload; keep log noise minimal for search.
            if "no matches found" in combined_clean.lower():
                self.log.emit("WARN  No matches found.")

        if returncode != 0:
            # Scoop uses code=1 for "no matches found" (similar to grep).
            if "no matches found" in combined_clean.lower():
                self.searched.emit([])
                # Treat as a successful search completion for UX.
                self.job_finished.emit(self._active_label, 0)
                return

            err_clean = self._sanitize_output(err).strip()
            if err_clean:
                self.log.emit(err_clean)

            self.error.emit(f"[error] scoop failed (code={returncode})")
            self.searched.emit([])
            self.job_finished.emit(self._active_label, returncode)
            return

        self.searched.emit(parse_scoop_search(out))
        self.job_finished.emit(self._active_label, 0)

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
            self.job_finished.emit(self._active_label, returncode)
            return

        if refresh_after:
            self._refresh_after_finish = True

        self.job_finished.emit(self._active_label, 0)
