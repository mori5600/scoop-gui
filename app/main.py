import json
import shutil
import subprocess
import sys
import re
from PySide6.QtCore import QObject, Qt, QSortFilterProxyModel, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QAbstractItemView, QApplication, QHeaderView, QMainWindow

try:
    from .ui_generated.ui_MainWindow import Ui_MainWindow
except ImportError:
    from app.ui_generated.ui_MainWindow import Ui_MainWindow


class _ScoopListWorker(QObject):
    finished = Signal(bytes, bytes, int)

    def __init__(self, shell: str, command: str):
        super().__init__()
        self._shell = shell
        self._command = command

    @Slot()
    def run(self):
        try:
            result = subprocess.run(
                [self._shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", self._command],
                capture_output=True,
            )
            self.finished.emit(result.stdout, result.stderr, result.returncode)
        except Exception as e:
            self.finished.emit(b"", str(e).encode("utf-8", errors="replace"), 1)


class ScoopClient:
    def __init__(self, ui, model, proxy):
        self.ui = ui
        self.model = model
        self.proxy = proxy

        self._thread: QThread | None = None
        self._worker: _ScoopListWorker | None = None

    def refresh_list(self):
        if self._thread is not None and self._thread.isRunning():
            self.ui.plainTextEditLog.appendPlainText("[info] already running")
            return

        self.ui.plainTextEditLog.appendPlainText("$ scoop export")
        self.ui.plainTextEditLog.appendPlainText("[running] ...")

        shell = shutil.which("pwsh") or shutil.which("powershell") or "powershell"
        # scoop export は最初から JSON（buckets/apps）を出力するので、テキスト解析より安定する
        # PowerShell の情報ストリームは 6> $null で抑制
        # exit $LASTEXITCODE で scoop の終了コードを PowerShell の終了コードに反映
        cmd = "$ErrorActionPreference='Stop'; scoop export 6> $null; exit $LASTEXITCODE"

        thread = QThread()
        worker = _ScoopListWorker(shell, cmd)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self._finished)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(self._thread_finished)
        self._thread = thread
        self._worker = worker
        thread.start()

    def _thread_finished(self):
        self._thread = None
        self._worker = None

    @staticmethod
    def _decode(data: bytes) -> str:
        for enc in ("utf-8", "cp932"):
            try:
                return data.decode(enc)
            except UnicodeDecodeError:
                continue
        return data.decode("utf-8", errors="replace")

    def _finished(self, stdout: bytes, stderr: bytes, returncode: int):
        out = self._decode(stdout)
        err = self._decode(stderr)
        if err.strip():
            self.ui.plainTextEditLog.appendPlainText(err.rstrip())

        if returncode != 0:
            self.ui.plainTextEditLog.appendPlainText(f"[error] scoop failed (code={returncode})")
            return

        rows = self._parse_scoop_list_json(out)
        if rows is None:
            rows = self._parse_scoop_list_text(out)
        if not rows:
            self.ui.plainTextEditLog.appendPlainText("[error] failed to parse scoop output")
            return

        # モデル更新
        self.model.removeRows(0, self.model.rowCount())
        for name, ver, source, updated, info in rows:
            self.model.appendRow(
                [
                    QStandardItem(name),
                    QStandardItem(ver),
                    QStandardItem(source),
                    QStandardItem(updated),
                    QStandardItem(info),
                ]
            )

        self.ui.tableViewPackages.resizeColumnsToContents()
        self.ui.plainTextEditLog.appendPlainText(f"[loaded] {len(rows)} packages")

        # 先頭を選択（任意）
        if self.proxy.rowCount() > 0:
            idx = self.proxy.index(0, 0)
            self.ui.tableViewPackages.setCurrentIndex(idx)

    @staticmethod
    def _parse_scoop_list_json(text: str):
        # scoop export は { "buckets": [...], "apps": [...] } 形式
        json_start = text.find("{")
        if json_start == -1:
            # 互換用（念のため）
            json_start = text.find("[")
        if json_start == -1:
            return None

        try:
            data = json.loads(text[json_start:])
        except json.JSONDecodeError:
            return None

        if isinstance(data, dict) and isinstance(data.get("apps"), list):
            items = data["apps"]
        elif isinstance(data, dict):
            items = [data]
        elif isinstance(data, list):
            items = data
        else:
            return None

        rows = []
        for item in items:
            if not isinstance(item, dict):
                continue
            name = str(item.get("Name", ""))
            ver = str(item.get("Version", ""))
            source = str(item.get("Source", ""))
            updated_raw = str(item.get("Updated", ""))
            info = str(item.get("Info", ""))

            updated = updated_raw[:19].replace("T", " ") if len(updated_raw) >= 19 else updated_raw
            rows.append((name, ver, source, updated, info))
        return rows or None

    @staticmethod
    def _parse_scoop_list_text(text: str):
        """
        ざっくり: 'name version source updated info...' を取る。
        ヘッダ行や罫線っぽい行は捨てる。
        """
        rows = []
        for line in text.splitlines():
            s = line.strip()
            if not s:
                continue
            if re.search(r"\bName\b", s) and re.search(r"\bVersion\b", s):
                continue
            if s.lower().startswith("installed apps"):
                continue
            if set(s.replace(" ", "")) <= set("-="):
                continue

            parts = s.split()
            if len(parts) < 2:
                continue

            name, ver = parts[0], parts[1]
            if ":" in name or ":" in ver:
                continue

            source = parts[2] if len(parts) >= 3 else ""
            updated = ""
            info = ""
            if len(parts) >= 5:
                updated = f"{parts[3]} {parts[4]}"
                info = " ".join(parts[5:]) if len(parts) >= 6 else ""
            elif len(parts) == 4:
                updated = parts[3]
            rows.append((name, ver, source, updated, info))
        return rows


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 1) splitterの初期比率（左320目安）
        self.ui.splitterMain.setSizes([320, 580])

        # 2) モデル
        self.model = QStandardItemModel(0, 5, self)
        self.model.setHorizontalHeaderLabels(["Name", "Version", "Source", "Updated", "Info"])

        # 3) 検索（proxyでフィルタ）
        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)  # type: ignore
        self.proxy.setFilterKeyColumn(0)  # Name列でフィルタ
        self.ui.tableViewPackages.setModel(self.proxy)

        self.ui.tableViewPackages.setSortingEnabled(True)
        self.ui.tableViewPackages.resizeColumnsToContents()

        # 4) 検索欄のイベント
        self.ui.lineEditSearch.textChanged.connect(self.proxy.setFilterFixedString)

        # 5) 選択 → Details更新
        sel = self.ui.tableViewPackages.selectionModel()
        sel.currentChanged.connect(self.on_current_changed)

        # 6) 初期表示
        self.set_details("-", "-")

        self.polish_table(self.ui)

        self.scoop = ScoopClient(self.ui, self.model, self.proxy)
        QTimer.singleShot(0, self.scoop.refresh_list)

    @staticmethod
    def polish_table(ui: Ui_MainWindow):
        tv = ui.tableViewPackages  # type: ignore

        # 行番号（縦ヘッダ）を消す
        tv.verticalHeader().setVisible(False)

        # 横ヘッダの挙動
        hh = tv.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setSectionResizeMode(0, QHeaderView.Stretch)  # type: ignore
        hh.setSectionResizeMode(
            1,
            QHeaderView.ResizeToContents,  # type: ignore
        )  # Version は内容に合わせる

        # 見た目・操作性
        tv.setWordWrap(False)
        tv.setAlternatingRowColors(True)
        tv.setShowGrid(False)
        tv.setSortingEnabled(True)

        # 余白が気になる場合（任意）
        tv.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tv.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def set_details(self, name: str, version: str):
        self.ui.labelNameValue.setText(name)
        self.ui.labelVersionValue.setText(version)

    def on_current_changed(self, current, previous):
        if not current.isValid():
            self.set_details("-", "-")
            return

        # proxy index -> source index
        src = self.proxy.mapToSource(current)
        name = self.model.item(src.row(), 0).text()
        ver = self.model.item(src.row(), 1).text()
        self.set_details(name, ver)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
