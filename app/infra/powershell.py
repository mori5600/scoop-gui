import shutil


def find_powershell_executable() -> str:
    """Finds a usable PowerShell executable.

    Prefers PowerShell 7 (`pwsh`) when available, otherwise falls back to Windows
    PowerShell (`powershell`).

    Returns:
        The executable path or name to use with subprocess.
    """
    return shutil.which("pwsh") or shutil.which("powershell") or "powershell"


def build_powershell_argv(command: str, shell: str | None = None) -> list[str]:
    """Builds an argv list to execute a PowerShell command.

    Args:
        command: PowerShell command string to execute.
        shell: PowerShell executable path/name. If omitted, it will be auto-detected.

    Returns:
        Argument vector suitable for `subprocess.run(...)`.
    """
    exe = shell or find_powershell_executable()
    return [
        exe,
        "-NoLogo",
        "-NoProfile",
        "-NonInteractive",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        command,
    ]
