# scoop-gui

Small Windows GUI for [Scoop](https://scoop.sh/) (Python + PySide6).

## Features

- View installed apps (via `scoop export`)
- Search apps (via `scoop search`)
- Install / Update / Uninstall / Cleanup

## Requirements

- Windows (win-64)
- Scoop installed and available as `scoop` in PowerShell
- [pixi](https://pixi.prefix.dev/latest/) for the dev environment

## Development

```powershell
pixi install
pixi run app
```

Useful tasks:

```powershell
pixi run check     # ruff + ty
pixi run format    # ruff --fix + ruff format
pixi run test      # pytest
pixi run designer  # Qt Designer
pixi run uic-all   # generate app/ui_generated/*.py from app/ui/*.ui
```

## Build

Builds a standalone executable with Nuitka:

```powershell
pixi run build
```

Output: `main.dist/scoop-gui.exe`
