from PySide6.QtCore import Qt, QSortFilterProxyModel, QTimer
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QMainWindow

from app.application.scoop_controller import ScoopController
from app.core.scoop_types import ScoopApp

try:
    from ..ui_generated.ui_MainWindow import Ui_MainWindow
except ImportError:
    from app.ui_generated.ui_MainWindow import Ui_MainWindow


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.splitterMain.setSizes([320, 580])

        self.model = QStandardItemModel(0, 5, self)
        self.model.setHorizontalHeaderLabels(
            ["Name", "Version", "Source", "Updated", "Info"]
        )

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseInsensitive)  # type: ignore
        self.proxy.setFilterKeyColumn(0)

        self.ui.tableViewPackages.setModel(self.proxy)
        self.ui.tableViewPackages.setSortingEnabled(True)

        self.ui.lineEditSearch.textChanged.connect(self.proxy.setFilterFixedString)

        selection_model = self.ui.tableViewPackages.selectionModel()
        selection_model.currentChanged.connect(self.on_current_changed)

        self.set_details("-", "-")
        self._polish_table()

        self.scoop = ScoopController(self)
        self.scoop.log.connect(self.ui.plainTextEditLog.appendPlainText)
        self.scoop.error.connect(self.ui.plainTextEditLog.appendPlainText)
        self.scoop.loaded.connect(self.on_packages_loaded)

        self.ui.pushButtonRefresh.clicked.connect(self.scoop.refresh_installed_apps)
        self.ui.pushButtonUninstall.clicked.connect(self.on_uninstall_clicked)
        self.ui.pushButtonUpdate.clicked.connect(self.on_update_clicked)
        self.ui.pushButtonCleanup.clicked.connect(self.on_cleanup_clicked)

        QTimer.singleShot(0, self.scoop.refresh_installed_apps)

    def _polish_table(self) -> None:
        """Applies initial table view settings."""
        tv = self.ui.tableViewPackages  # type: ignore

        tv.verticalHeader().setVisible(False)

        hh = tv.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setSectionResizeMode(0, QHeaderView.Stretch)  # type: ignore
        hh.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # type: ignore
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # type: ignore
        hh.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # type: ignore

        tv.setWordWrap(False)
        tv.setAlternatingRowColors(True)
        tv.setShowGrid(False)
        tv.setSortingEnabled(True)
        tv.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tv.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def on_packages_loaded(self, apps_obj: object) -> None:
        """Updates the table model from loaded Scoop apps.

        Args:
            apps_obj: List of `ScoopApp` instances (passed via Qt signals).
        """
        apps = apps_obj if isinstance(apps_obj, list) else []

        tv = self.ui.tableViewPackages
        sorting_was_enabled = tv.isSortingEnabled()
        tv.setSortingEnabled(False)

        self.model.setRowCount(0)
        for app in apps:
            if not isinstance(app, ScoopApp):
                continue
            self.model.appendRow(
                [
                    QStandardItem(app.name),
                    QStandardItem(app.version),
                    QStandardItem(app.source),
                    QStandardItem(app.updated),
                    QStandardItem(app.info),
                ]
            )

        tv.resizeColumnsToContents()
        tv.setSortingEnabled(sorting_was_enabled)

        if self.proxy.rowCount() > 0:
            idx = self.proxy.index(0, 0)
            self.ui.tableViewPackages.setCurrentIndex(idx)
        else:
            self.set_details("-", "-")

    def set_details(self, name: str, version: str) -> None:
        """Updates the details panel.

        Args:
            name: App name to display.
            version: App version to display.
        """
        self.ui.labelNameValue.setText(name)
        self.ui.labelVersionValue.setText(version)

    def on_current_changed(self, current, previous) -> None:
        """Handles selection changes in the packages table."""
        if not current.isValid():
            self.set_details("-", "-")
            return

        src = self.proxy.mapToSource(current)
        name = self.model.item(src.row(), 0).text()
        ver = self.model.item(src.row(), 1).text()
        self.set_details(name, ver)

    def _selected_app_name(self) -> str | None:
        """Returns the currently selected app name, if any."""
        current = self.ui.tableViewPackages.currentIndex()
        if not current.isValid():
            return None

        src = self.proxy.mapToSource(current)
        item = self.model.item(src.row(), 0)
        if item is None:
            return None

        name = item.text().strip()
        return name or None

    def _require_selection(self, action: str) -> str | None:
        """Returns the selected app name or logs a hint message."""
        name = self._selected_app_name()
        if not name:
            self.scoop.log.emit(f"[info] select a package to {action}")
            return None
        return name

    def on_uninstall_clicked(self) -> None:
        """Runs scoop uninstall for the selected app."""
        name = self._require_selection("uninstall")
        if not name:
            return
        self.scoop.uninstall_app(name)

    def on_update_clicked(self) -> None:
        """Runs scoop update for the selected app."""
        name = self._require_selection("update")
        if not name:
            return
        self.scoop.update_app(name)

    def on_cleanup_clicked(self) -> None:
        """Runs scoop cleanup for all apps."""
        self.scoop.cleanup_all()
