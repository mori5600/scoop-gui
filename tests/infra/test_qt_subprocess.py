import subprocess

from app.infra import qt_subprocess
from app.infra.qt_subprocess import SubprocessWorker


class _DummyCompletedProcess:
    def __init__(self, stdout: bytes, stderr: bytes, returncode: int) -> None:
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def _capture_finished(worker: SubprocessWorker) -> list[tuple[bytes, bytes, int]]:
    captured: list[tuple[bytes, bytes, int]] = []
    worker.finished.connect(lambda out, err, code: captured.append((out, err, code)))
    return captured


def test_run_emits_subprocess_result_on_non_windows(monkeypatch) -> None:
    monkeypatch.setattr(qt_subprocess.os, "name", "posix", raising=False)

    def fake_run(argv: list[str], **kwargs: dict) -> _DummyCompletedProcess:
        assert argv == ["example", "arg"]
        assert kwargs == {"capture_output": True, "timeout": 15}
        return _DummyCompletedProcess(b"stdout", b"stderr", 3)

    monkeypatch.setattr(qt_subprocess.subprocess, "run", fake_run)
    worker = SubprocessWorker(argv=["example", "arg"], timeout_sec=15)
    captured = _capture_finished(worker)

    worker.run()

    assert captured == [(b"stdout", b"stderr", 3)]


def test_run_adds_creationflags_on_windows(monkeypatch) -> None:
    monkeypatch.setattr(qt_subprocess.os, "name", "nt", raising=False)

    def fake_run(argv: list[str], **kwargs: dict) -> _DummyCompletedProcess:
        assert argv == ["example"]
        assert kwargs == {
            "capture_output": True,
            "timeout": 8,
            "creationflags": qt_subprocess._CREATE_NO_WINDOW,
        }
        return _DummyCompletedProcess(b"", b"", 0)

    monkeypatch.setattr(qt_subprocess.subprocess, "run", fake_run)
    worker = SubprocessWorker(argv=["example"], timeout_sec=8)
    captured = _capture_finished(worker)

    worker.run()

    assert captured == [(b"", b"", 0)]


def test_run_emits_timeout_payload_when_timeout_expired(monkeypatch) -> None:
    def fake_run(argv: list[str], **kwargs: object) -> _DummyCompletedProcess:
        timeout = kwargs.get("timeout")
        assert isinstance(timeout, (int, float))
        raise subprocess.TimeoutExpired(cmd=argv, timeout=timeout)

    monkeypatch.setattr(qt_subprocess.subprocess, "run", fake_run)
    worker = SubprocessWorker(argv=["slow-command"], timeout_sec=4)
    captured = _capture_finished(worker)

    worker.run()

    assert captured == [(b"", b"timeout: command exceeded limit", 124)]


def test_run_emits_error_payload_when_unexpected_exception_occurs(monkeypatch) -> None:
    def fake_run(argv: list[str], **kwargs: dict) -> _DummyCompletedProcess:
        raise RuntimeError("unexpected failure")

    monkeypatch.setattr(qt_subprocess.subprocess, "run", fake_run)
    worker = SubprocessWorker(argv=["broken-command"], timeout_sec=4)
    captured = _capture_finished(worker)

    worker.run()

    assert captured == [(b"", b"unexpected failure", 1)]
