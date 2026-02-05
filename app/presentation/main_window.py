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
from app.core.scoop_types import ScoopApp, ScoopSearchResult

try:
    from ..ui_generated.ui_MainWindow import Ui_MainWindow
except ImportError:
    from app.ui_generated.ui_MainWindow import Ui_MainWindow


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self._busy = False
        self._installed_initial_sort_applied = False
        self._discover_splitter_polished = False

        self._installed_names: set[str] = set()
        self._pending_select_installed_name: str | None = None
        self._pending_switch_to_installed = False

        self._last_discover_query = ""
        self._pending_discover_query: str | None = None

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.tabWidgetMain.currentChanged.connect(self.on_tab_changed)

        # ---- Installed tab
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
        selection_model.currentChanged.connect(self.on_installed_current_changed)

        self.set_installed_details("-", "-")
        self._polish_installed_table()

        # ---- Discover tab
        self.discover_model = QStandardItemModel(0, 4, self)
        self.discover_model.setHorizontalHeaderLabels(
            ["Name", "Version", "Source", "Binaries"]
        )
        self.ui.tableViewDiscover.setModel(self.discover_model)
        self.ui.tableViewDiscover.setSortingEnabled(True)
        self.ui.tableViewDiscover.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        discover_sel = self.ui.tableViewDiscover.selectionModel()
        discover_sel.currentChanged.connect(self.on_discover_current_changed)
        self.ui.tableViewDiscover.doubleClicked.connect(
            lambda _idx: self.on_discover_install_clicked()
        )

        self.set_discover_details("-", "-", "-", "-")
        self._polish_discover_table()
        self.ui.pushButtonInstall.setEnabled(False)

        self.ui.lineEditDiscoverSearch.textChanged.connect(
            self._on_discover_query_changed
        )
        self.ui.lineEditDiscoverSearch.returnPressed.connect(
            self.on_discover_search_clicked
        )
        self.ui.pushButtonDiscoverSearch.clicked.connect(
            self.on_discover_search_clicked
        )

        # ---- Controller + wiring
        self.scoop = ScoopController(self)
        self.scoop.log.connect(self.ui.plainTextEditLog.appendPlainText)
        self.scoop.error.connect(self.ui.plainTextEditLog.appendPlainText)
        self.scoop.loaded.connect(self.on_packages_loaded)
        self.scoop.searched.connect(self.on_search_loaded)
        self.scoop.busy_changed.connect(self.on_busy_changed)
        self.scoop.job_started.connect(self.on_job_started)
        self.scoop.job_finished.connect(self.on_job_finished)

        self.ui.pushButtonRefresh.clicked.connect(self.scoop.refresh_installed_apps)
        self.ui.pushButtonUninstall.clicked.connect(self.on_uninstall_clicked)
        self.ui.pushButtonUpdate.clicked.connect(self.on_update_clicked)
        self.ui.pushButtonCleanup.clicked.connect(self.on_cleanup_clicked)

        self.ui.pushButtonInstall.clicked.connect(self.on_discover_install_clicked)

        self._setup_update_menu()
        self._setup_cleanup_menu()

        QTimer.singleShot(0, self._set_initial_splitter_sizes)
        QTimer.singleShot(0, self.scoop.refresh_installed_apps)

    def _polish_installed_table(self) -> None:
        """Applies initial settings to the Installed table."""
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

    def _polish_discover_table(self) -> None:
        """Applies initial settings to the Discover table."""
        tv = self.ui.tableViewDiscover

        tv.verticalHeader().setVisible(False)

        hh = tv.horizontalHeader()
        hh.setStretchLastSection(True)
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hh.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hh.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)

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
        """Applies a pleasant initial splitter sizing on first paint."""
        # Root: tabs vs log (roughly 70:30)
        root = self.ui.splitterRoot
        root.setStretchFactor(0, 3)
        root.setStretchFactor(1, 1)
        total_h = root.size().height() or self.height()
        top_h = max(1, int(total_h * 0.72))
        root.setSizes([top_h, max(1, total_h - top_h)])

        # Installed: list vs details (50:50)
        sp = self.ui.splitterMain
        sp.setStretchFactor(0, 1)
        sp.setStretchFactor(1, 1)
        total_w = sp.size().width() or self.width()
        half = max(1, total_w // 2)
        sp.setSizes([half, half])

    def _polish_discover_splitter_once(self) -> None:
        """Sizes the Discover splitter the first time the tab is shown."""
        if self._discover_splitter_polished:
            return
        sp = self.ui.splitterDiscover
        sp.setStretchFactor(0, 1)
        sp.setStretchFactor(1, 1)
        total_w = sp.size().width() or self.width()
        half = max(1, total_w // 2)
        sp.setSizes([half, half])
        self._discover_splitter_polished = True

    def on_tab_changed(self, _index: int) -> None:
        current = self.ui.tabWidgetMain.currentWidget()
        if current is self.ui.tabDiscover:
            self._polish_discover_splitter_once()
            self.ui.lineEditDiscoverSearch.setFocus()

            # If the user explicitly requested a search while a job was running,
            # run it when the tab becomes visible and we're idle again.
            if (
                (not self._busy)
                and self._pending_discover_query
                and self._pending_discover_query
                == self.ui.lineEditDiscoverSearch.text().strip()
            ):
                self.ui.labelDiscoverStatus.setText("Searching...")
                self.scoop.search_apps(self._pending_discover_query)
                self._pending_discover_query = None
        else:
            self.ui.lineEditSearch.setFocus()

    def on_packages_loaded(self, apps_obj: object) -> None:
        """Updates the table model from loaded Scoop apps.

        Args:
            apps_obj: List of `ScoopApp` instances (passed via Qt signals).
        """
        apps = apps_obj if isinstance(apps_obj, list) else []
        self._installed_names = {
            app.name for app in apps if isinstance(app, ScoopApp) and app.name
        }

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
        if not self._installed_initial_sort_applied:
            section, order = 0, Qt.SortOrder.AscendingOrder
            hh.setSortIndicator(section, order)
            self._installed_initial_sort_applied = True
        tv.sortByColumn(section, order)

        if self._pending_select_installed_name:
            # Switch + select after install.
            name = self._pending_select_installed_name
            switch = self._pending_switch_to_installed
            self._pending_select_installed_name = None
            self._pending_switch_to_installed = False
            if not self.show_installed_app(name, switch_tab=switch):
                # Fallback: keep something selected to populate the details panel.
                if self.proxy.rowCount() > 0:
                    idx = self.proxy.index(0, 0)
                    self.ui.tableViewPackages.setCurrentIndex(idx)
                else:
                    self.set_installed_details("-", "-")
        else:
            if self.proxy.rowCount() > 0:
                idx = self.proxy.index(0, 0)
                self.ui.tableViewPackages.setCurrentIndex(idx)
            else:
                self.set_installed_details("-", "-")

        self._sync_discover_install_button()

    def set_installed_details(self, name: str, version: str) -> None:
        """Updates the Installed details panel.

        Args:
            name: App name to display.
            version: App version to display.
        """
        self.ui.labelNameValue.setText(name)
        self.ui.labelVersionValue.setText(version)

    def set_discover_details(
        self, name: str, version: str, source: str, binaries: str
    ) -> None:
        """Updates the Discover details panel."""
        self.ui.labelDiscoverNameValue.setText(name)
        self.ui.labelDiscoverVersionValue.setText(version)
        self.ui.labelDiscoverSourceValue.setText(source)
        self.ui.labelDiscoverBinariesValue.setText(binaries)

    def on_installed_current_changed(self, current, previous) -> None:
        """Handles selection changes in the Installed table."""
        if not current.isValid():
            self.set_installed_details("-", "-")
            return

        src = self.proxy.mapToSource(current)
        name = self.model.item(src.row(), 0).text()
        ver = self.model.item(src.row(), 1).text()
        self.set_installed_details(name, ver)

    def _selected_installed_app_name(self) -> str | None:
        """Returns the selected Installed app name, if any."""
        current = self.ui.tableViewPackages.currentIndex()
        if not current.isValid():
            return None

        src = self.proxy.mapToSource(current)
        item = self.model.item(src.row(), 0)
        if item is None:
            return None

        name = item.text().strip()
        return name or None

    def _require_installed_selection(self, action: str) -> str | None:
        """Returns the selected Installed app name or logs a hint message."""
        name = self._selected_installed_app_name()
        if not name:
            self.scoop.log.emit(f"[info] select a package to {action}")
            return None
        return name

    def show_installed_app(self, name: str, switch_tab: bool) -> bool:
        """Selects an Installed row by app name, if present."""
        if switch_tab:
            self.ui.tabWidgetMain.setCurrentWidget(self.ui.tabInstalled)

        # Ensure it isn't hidden by the filter.
        self.ui.lineEditSearch.setText("")

        for row in range(self.model.rowCount()):
            item = self.model.item(row, 0)
            if item is None:
                continue
            if item.text().strip() != name:
                continue

            src_idx = self.model.index(row, 0)
            idx = self.proxy.mapFromSource(src_idx)
            if idx.isValid():
                self.ui.tableViewPackages.setCurrentIndex(idx)
                self.ui.tableViewPackages.scrollTo(idx)
                return True

        self.scoop.log.emit(f"[info] '{name}' not found in Installed list")
        return False

    def on_uninstall_clicked(self) -> None:
        """Runs scoop uninstall for the selected app."""
        name = self._require_installed_selection("uninstall")
        if not name:
            return
        self.scoop.uninstall_app(name)

    def on_update_clicked(self) -> None:
        """Runs scoop update for the selected app."""
        name = self._require_installed_selection("update")
        if not name:
            return
        self.scoop.update_app(name)

    def on_update_all_clicked(self) -> None:
        """Runs scoop update for all apps."""
        self.scoop.update_all_apps()

    def on_cleanup_clicked(self) -> None:
        """Runs scoop cleanup for the selected app."""
        name = self._require_installed_selection("cleanup")
        if not name:
            return
        self.scoop.cleanup_app(name)

    def on_cleanup_all_clicked(self) -> None:
        """Runs scoop cleanup for all apps."""
        self.scoop.cleanup_all()

    # ---- Discover
    def _on_discover_query_changed(self, _text: str) -> None:
        """Updates Discover UI state when the query text changes.

        Important: this must NOT trigger `scoop search` automatically. Users are expected to
        click the Search button (or press Enter) to run the search explicitly.
        """
        query = self.ui.lineEditDiscoverSearch.text().strip()
        self._pending_discover_query = None

        if len(query) < 2:
            self.ui.labelDiscoverStatus.setText(
                "Type at least 2 characters, then click Search"
            )
        else:
            self.ui.labelDiscoverStatus.setText("Ready. Click Search")

        # Prevent stale results from looking like they match the new query.
        if query != self._last_discover_query:
            self.discover_model.setRowCount(0)
            self.set_discover_details("-", "-", "-", "-")
            self._sync_discover_install_button()

    def on_discover_search_clicked(self) -> None:
        self._run_discover_search()

    def _run_discover_search(self) -> None:
        query = self.ui.lineEditDiscoverSearch.text().strip()
        if len(query) < 2:
            self._last_discover_query = ""
            self._pending_discover_query = None
            self.ui.labelDiscoverStatus.setText(
                "Type at least 2 characters, then click Search"
            )
            self.discover_model.setRowCount(0)
            self.set_discover_details("-", "-", "-", "-")
            self._sync_discover_install_button()
            return

        self._last_discover_query = query

        if self._busy:
            self._pending_discover_query = query
            self.ui.labelDiscoverStatus.setText("Busy... waiting to search")
            return

        self._pending_discover_query = None
        self.ui.labelDiscoverStatus.setText("Searching...")
        self.scoop.search_apps(query)

    def on_search_loaded(self, results_obj: object) -> None:
        results = results_obj if isinstance(results_obj, list) else []

        tv = self.ui.tableViewDiscover
        sorting_was_enabled = tv.isSortingEnabled()
        tv.setSortingEnabled(False)

        self.discover_model.setRowCount(0)
        for r in results:
            if not isinstance(r, ScoopSearchResult):
                continue
            self.discover_model.appendRow(
                [
                    QStandardItem(r.name),
                    QStandardItem(r.version),
                    QStandardItem(r.source),
                    QStandardItem(r.binaries),
                ]
            )

        tv.resizeColumnsToContents()
        tv.setSortingEnabled(sorting_was_enabled)

        if self.discover_model.rowCount() > 0:
            tv.setCurrentIndex(self.discover_model.index(0, 0))
            self.ui.labelDiscoverStatus.setText(
                f"{self.discover_model.rowCount()} results"
            )
        else:
            self.set_discover_details("-", "-", "-", "-")
            self.ui.labelDiscoverStatus.setText("No results")

        self._sync_discover_install_button()

    def on_discover_current_changed(self, current, previous) -> None:
        if not current.isValid():
            self.set_discover_details("-", "-", "-", "-")
            self._sync_discover_install_button()
            return

        row = current.row()
        name = self.discover_model.item(row, 0).text()
        version = self.discover_model.item(row, 1).text()
        source = self.discover_model.item(row, 2).text()
        binaries = self.discover_model.item(row, 3).text()
        self.set_discover_details(
            name or "-", version or "-", source or "-", binaries or "-"
        )
        self._sync_discover_install_button()

    def _selected_discover_app_name(self) -> str | None:
        current = self.ui.tableViewDiscover.currentIndex()
        if not current.isValid():
            return None
        item = self.discover_model.item(current.row(), 0)
        if item is None:
            return None
        name = item.text().strip()
        return name or None

    def _sync_discover_install_button(self) -> None:
        btn = self.ui.pushButtonInstall
        if self._busy:
            btn.setEnabled(False)
            return

        name = self._selected_discover_app_name()
        if not name:
            btn.setText("Install")
            btn.setEnabled(False)
            return

        if name in self._installed_names:
            btn.setText("Show Installed")
        else:
            btn.setText("Install")
        btn.setEnabled(True)

    def on_discover_install_clicked(self) -> None:
        name = self._selected_discover_app_name()
        if not name:
            self.scoop.log.emit("[info] select an app to install")
            return

        if name in self._installed_names:
            self.show_installed_app(name, switch_tab=True)
            return

        self._pending_select_installed_name = name
        self._pending_switch_to_installed = True
        self.scoop.install_app(name)

    # ---- Busy/state
    def on_busy_changed(self, busy: bool) -> None:
        self._busy = busy
        self.ui.pushButtonRefresh.setEnabled(not busy)
        self.ui.pushButtonUninstall.setEnabled(not busy)
        self.ui.pushButtonUpdate.setEnabled(not busy)
        self.ui.pushButtonCleanup.setEnabled(not busy)
        self._sync_discover_install_button()

        if not busy and self._pending_discover_query:
            # Run a queued search after long-running jobs finish.
            if self.ui.tabWidgetMain.currentWidget() is self.ui.tabDiscover:
                # Keep the newest query only.
                if (
                    self._pending_discover_query
                    == self.ui.lineEditDiscoverSearch.text().strip()
                ):
                    self.ui.labelDiscoverStatus.setText("Searching...")
                    self.scoop.search_apps(self._pending_discover_query)
                    self._pending_discover_query = None

    def on_job_started(self, label: str) -> None:
        self.statusBar().showMessage(f"Running: {label}")

    def on_job_finished(self, label: str, returncode: int) -> None:
        if returncode == 0:
            self.statusBar().showMessage(f"Done: {label}", 2000)
        else:
            self.statusBar().showMessage(f"Failed: {label} (code={returncode})", 4000)

        if label.startswith("scoop install ") and returncode != 0:
            self._pending_select_installed_name = None
            self._pending_switch_to_installed = False
