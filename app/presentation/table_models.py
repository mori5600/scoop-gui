from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt

from app.core.scoop_types import ScoopApp, ScoopSearchResult


class DiscoverTableModel(QAbstractTableModel):
    """Lightweight table model backed by ScoopSearchResult rows."""

    _HEADERS = ("Name", "Version", "Source", "Binaries")

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[ScoopSearchResult] = []

    def rowCount(
        self,
        /,
        parent: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        if parent.isValid():
            return 0
        return len(self._rows)

    def columnCount(
        self,
        /,
        parent: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        if parent.isValid():
            return 0
        return len(self._HEADERS)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        /,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> object | None:
        if not index.isValid():
            return None
        if role not in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return None

        row = self._rows[index.row()]
        column = index.column()
        if column == 0:
            return row.name
        if column == 1:
            return row.version
        if column == 2:
            return row.source
        if column == 3:
            return row.binaries
        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation != Qt.Orientation.Horizontal:
            return None
        if 0 <= section < len(self._HEADERS):
            return self._HEADERS[section]
        return None

    def set_results(self, rows: list[ScoopSearchResult]) -> None:
        self.beginResetModel()
        self._rows = list(rows)
        self.endResetModel()

    def result_at(self, row: int) -> ScoopSearchResult | None:
        if 0 <= row < len(self._rows):
            return self._rows[row]
        return None

    def sort(
        self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder
    ) -> None:
        if not self._rows:
            return
        key_map = {
            0: lambda r: r.name.casefold(),
            1: lambda r: r.version.casefold(),
            2: lambda r: r.source.casefold(),
            3: lambda r: r.binaries.casefold(),
        }
        key_func = key_map.get(column)
        if key_func is None:
            return
        reverse = order == Qt.SortOrder.DescendingOrder
        self.layoutAboutToBeChanged.emit()
        self._rows.sort(key=key_func, reverse=reverse)
        self.layoutChanged.emit()


class InstalledTableModel(QAbstractTableModel):
    """Lightweight table model backed by installed ScoopApp rows."""

    _HEADERS = ("Name", "Version", "Source", "Updated", "Info")

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[ScoopApp] = []
        self._name_to_row: dict[str, int] = {}

    def rowCount(
        self,
        /,
        parent: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        if parent.isValid():
            return 0
        return len(self._rows)

    def columnCount(
        self,
        /,
        parent: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        if parent.isValid():
            return 0
        return len(self._HEADERS)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        /,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> object | None:
        if not index.isValid():
            return None
        if role not in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return None

        row = self._rows[index.row()]
        column = index.column()
        if column == 0:
            return row.name
        if column == 1:
            return row.version
        if column == 2:
            return row.source
        if column == 3:
            return row.updated
        if column == 4:
            return row.info
        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation != Qt.Orientation.Horizontal:
            return None
        if 0 <= section < len(self._HEADERS):
            return self._HEADERS[section]
        return None

    def set_apps(self, rows: list[ScoopApp]) -> None:
        self.beginResetModel()
        self._rows = list(rows)
        self._name_to_row = {}
        for index, app in enumerate(self._rows):
            if app.name and app.name not in self._name_to_row:
                self._name_to_row[app.name] = index
        self.endResetModel()

    def app_at(self, row: int) -> ScoopApp | None:
        if 0 <= row < len(self._rows):
            return self._rows[row]
        return None

    def row_for_name(self, name: str) -> int | None:
        return self._name_to_row.get(name)
