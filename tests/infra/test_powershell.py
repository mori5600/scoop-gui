from app.infra import powershell
from app.infra.powershell import build_powershell_argv, find_powershell_executable


def test_find_powershell_executable_prefers_pwsh(monkeypatch) -> None:
    def fake_which(name: str) -> str | None:
        mapping = {
            "pwsh": "C:/tools/pwsh.exe",
            "powershell": "C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
        }
        return mapping.get(name)

    monkeypatch.setattr(powershell.shutil, "which", fake_which)

    assert find_powershell_executable() == "C:/tools/pwsh.exe"


def test_find_powershell_executable_falls_back_to_powershell(monkeypatch) -> None:
    def fake_which(name: str) -> str | None:
        mapping = {
            "pwsh": None,
            "powershell": "C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
        }
        return mapping.get(name)

    monkeypatch.setattr(powershell.shutil, "which", fake_which)

    assert (
        find_powershell_executable()
        == "C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
    )


def test_find_powershell_executable_uses_literal_default_when_not_found(
    monkeypatch,
) -> None:
    monkeypatch.setattr(powershell.shutil, "which", lambda _: None)

    assert find_powershell_executable() == "powershell"


def test_build_powershell_argv_uses_provided_shell() -> None:
    argv = build_powershell_argv("Write-Output 'ok'", shell="pwsh")

    assert argv == [
        "pwsh",
        "-NoLogo",
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        "Write-Output 'ok'",
    ]


def test_build_powershell_argv_uses_auto_detected_shell(monkeypatch) -> None:
    monkeypatch.setattr(
        powershell, "find_powershell_executable", lambda: "C:/tools/pwsh.exe"
    )

    argv = build_powershell_argv("Write-Output 'ok'")

    assert argv[0] == "C:/tools/pwsh.exe"
