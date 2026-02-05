from PySide6.QtCore import QSortFilterProxyModel, Qt, QTimer
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QMainWindow,
    QMenu,
    QToolButton,
)

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
        self._initial_sort_applied = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.model = QStandardItemModel(0, 5, self)
        self.model.setHorizontalHeaderLabels(
            ["Name", "Version", "Source", "Updated", "Info"]
        )

        self.proxy = QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.proxy.setFilterKeyColumn(0)

        self.ui.tableViewPackages.setModel(self.proxy)
        self.ui.tableViewPackages.setSortingEnabled(True)
        # Default initial ordering: Name ascending.
        self.ui.tableViewPackages.sortByColumn(0, Qt.SortOrder.AscendingOrder)

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

        self._setup_update_menu()
        self._setup_cleanup_menu()

        QTimer.singleShot(0, self._set_initial_splitter_sizes)
        QTimer.singleShot(0, self.scoop.refresh_installed_apps)

    def _polish_table(self) -> None:
        """Applies initial table view settings."""
        tv = self.ui.tableViewPackages

        tv.verticalHeader().setVisible(False)

        hh = tv.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        tv.setWordWrap(False)
        tv.setAlternatingRowColors(True)
        tv.setShowGrid(False)
        tv.setSortingEnabled(True)
        tv.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        tv.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

    def _setup_update_menu(self) -> None:
        """Adds a compact menu to the Update button (e.g. "Update all")."""
        btn = self.ui.pushButtonUpdate
        if not isinstance(btn, QToolButton):
            # Keep startup resilient even if the .ui wasn't regenerated yet.
            return

        menu = QMenu(btn)
        action_update_all = menu.addAction("Update All")
        action_update_all.triggered.connect(self.on_update_all_clicked)

        btn.setMenu(menu)
        btn.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)

    def _setup_cleanup_menu(self) -> None:
        """Adds a compact menu to the Cleanup button (e.g. "Cleanup all")."""
        btn = self.ui.pushButtonCleanup
        if not isinstance(btn, QToolButton):
            # Keep startup resilient even if the .ui wasn't regenerated yet.
            return

        menu = QMenu(btn)
        action_cleanup_all = menu.addAction("Cleanup All")
        action_cleanup_all.triggered.connect(self.on_cleanup_all_clicked)

        btn.setMenu(menu)
        btn.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)

    def _set_initial_splitter_sizes(self) -> None:
        """Shows the left/right panes at ~50:50 on first paint."""
        sp = self.ui.splitterMain
        sp.setStretchFactor(0, 1)
        sp.setStretchFactor(1, 1)

        total = sp.size().width()
        if total <= 0:
            total = self.width()

        half = max(1, total // 2)
        sp.setSizes([half, half])

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

        # Re-apply sorting after repopulating the model.
        # First load defaults to Name ascending; later loads keep the current sort selection.
        hh = tv.horizontalHeader()
        section = hh.sortIndicatorSection()
        order = hh.sortIndicatorOrder()
        if not self._initial_sort_applied:
            section, order = 0, Qt.SortOrder.AscendingOrder
            hh.setSortIndicator(section, order)
            self._initial_sort_applied = True
        tv.sortByColumn(section, order)

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

    def on_update_all_clicked(self) -> None:
        """Runs scoop update for all apps."""
        self.scoop.update_all_apps()

    def on_cleanup_clicked(self) -> None:
        """Runs scoop cleanup for the selected app."""
        name = self._require_selection("cleanup")
        if not name:
            return
        self.scoop.cleanup_app(name)

    def on_cleanup_all_clicked(self) -> None:
        """Runs scoop cleanup for all apps."""
        self.scoop.cleanup_all()
