# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenuBar,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QTableView,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(900, 600)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutMain = QVBoxLayout(self.centralwidget)
        self.verticalLayoutMain.setSpacing(8)
        self.verticalLayoutMain.setObjectName("verticalLayoutMain")
        self.verticalLayoutMain.setContentsMargins(8, 8, 8, 8)
        self.splitterRoot = QSplitter(self.centralwidget)
        self.splitterRoot.setObjectName("splitterRoot")
        self.splitterRoot.setOrientation(Qt.Vertical)
        self.tabWidgetMain = QTabWidget(self.splitterRoot)
        self.tabWidgetMain.setObjectName("tabWidgetMain")
        self.tabInstalled = QWidget()
        self.tabInstalled.setObjectName("tabInstalled")
        self.horizontalLayoutInstalled = QHBoxLayout(self.tabInstalled)
        self.horizontalLayoutInstalled.setSpacing(0)
        self.horizontalLayoutInstalled.setObjectName("horizontalLayoutInstalled")
        self.horizontalLayoutInstalled.setContentsMargins(0, 0, 0, 0)
        self.splitterMain = QSplitter(self.tabInstalled)
        self.splitterMain.setObjectName("splitterMain")
        self.splitterMain.setOrientation(Qt.Horizontal)
        self.widgetLeft = QWidget(self.splitterMain)
        self.widgetLeft.setObjectName("widgetLeft")
        self.widgetLeft.setMinimumSize(QSize(320, 0))
        self.verticalLayoutLeft = QVBoxLayout(self.widgetLeft)
        self.verticalLayoutLeft.setSpacing(6)
        self.verticalLayoutLeft.setObjectName("verticalLayoutLeft")
        self.verticalLayoutLeft.setContentsMargins(0, 0, 0, 0)
        self.lineEditSearch = QLineEdit(self.widgetLeft)
        self.lineEditSearch.setObjectName("lineEditSearch")
        self.lineEditSearch.setClearButtonEnabled(True)

        self.verticalLayoutLeft.addWidget(self.lineEditSearch)

        self.tableViewPackages = QTableView(self.widgetLeft)
        self.tableViewPackages.setObjectName("tableViewPackages")
        self.tableViewPackages.setAlternatingRowColors(True)
        self.tableViewPackages.setShowGrid(False)
        self.tableViewPackages.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableViewPackages.setSelectionMode(QAbstractItemView.SingleSelection)

        self.verticalLayoutLeft.addWidget(self.tableViewPackages)

        self.splitterMain.addWidget(self.widgetLeft)
        self.widgetRight = QWidget(self.splitterMain)
        self.widgetRight.setObjectName("widgetRight")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widgetRight.sizePolicy().hasHeightForWidth())
        self.widgetRight.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QVBoxLayout(self.widgetRight)
        self.verticalLayout_2.setSpacing(8)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.groupBoxDetails = QGroupBox(self.widgetRight)
        self.groupBoxDetails.setObjectName("groupBoxDetails")
        self.groupBoxDetails.setMaximumSize(QSize(16777215, 200))
        self.formLayoutDetails = QFormLayout(self.groupBoxDetails)
        self.formLayoutDetails.setObjectName("formLayoutDetails")
        self.formLayoutDetails.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.formLayoutDetails.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.formLayoutDetails.setFormAlignment(Qt.AlignTop)
        self.formLayoutDetails.setHorizontalSpacing(12)
        self.formLayoutDetails.setVerticalSpacing(6)
        self.formLayoutDetails.setContentsMargins(8, 8, 8, 8)
        self.labelName = QLabel(self.groupBoxDetails)
        self.labelName.setObjectName("labelName")

        self.formLayoutDetails.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.labelName
        )

        self.labelNameValue = QLabel(self.groupBoxDetails)
        self.labelNameValue.setObjectName("labelNameValue")
        sizePolicy.setHeightForWidth(
            self.labelNameValue.sizePolicy().hasHeightForWidth()
        )
        self.labelNameValue.setSizePolicy(sizePolicy)
        self.labelNameValue.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.formLayoutDetails.setWidget(
            0, QFormLayout.ItemRole.FieldRole, self.labelNameValue
        )

        self.labelVersion = QLabel(self.groupBoxDetails)
        self.labelVersion.setObjectName("labelVersion")

        self.formLayoutDetails.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.labelVersion
        )

        self.labelVersionValue = QLabel(self.groupBoxDetails)
        self.labelVersionValue.setObjectName("labelVersionValue")
        sizePolicy.setHeightForWidth(
            self.labelVersionValue.sizePolicy().hasHeightForWidth()
        )
        self.labelVersionValue.setSizePolicy(sizePolicy)
        self.labelVersionValue.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.formLayoutDetails.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.labelVersionValue
        )

        self.verticalLayout_2.addWidget(self.groupBoxDetails)

        self.groupBoxActions = QGroupBox(self.widgetRight)
        self.groupBoxActions.setObjectName("groupBoxActions")
        self.horizontalLayoutActions = QHBoxLayout(self.groupBoxActions)
        self.horizontalLayoutActions.setSpacing(8)
        self.horizontalLayoutActions.setObjectName("horizontalLayoutActions")
        self.horizontalLayoutActions.setContentsMargins(8, 8, 8, 8)
        self.pushButtonRefresh = QPushButton(self.groupBoxActions)
        self.pushButtonRefresh.setObjectName("pushButtonRefresh")

        self.horizontalLayoutActions.addWidget(self.pushButtonRefresh)

        self.pushButtonUninstall = QPushButton(self.groupBoxActions)
        self.pushButtonUninstall.setObjectName("pushButtonUninstall")

        self.horizontalLayoutActions.addWidget(self.pushButtonUninstall)

        self.pushButtonUpdate = QToolButton(self.groupBoxActions)
        self.pushButtonUpdate.setObjectName("pushButtonUpdate")

        self.horizontalLayoutActions.addWidget(self.pushButtonUpdate)

        self.pushButtonCleanup = QToolButton(self.groupBoxActions)
        self.pushButtonCleanup.setObjectName("pushButtonCleanup")

        self.horizontalLayoutActions.addWidget(self.pushButtonCleanup)

        self.horizontalSpacerActions = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayoutActions.addItem(self.horizontalSpacerActions)

        self.verticalLayout_2.addWidget(self.groupBoxActions)

        self.verticalSpacerInstalled = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_2.addItem(self.verticalSpacerInstalled)

        self.splitterMain.addWidget(self.widgetRight)

        self.horizontalLayoutInstalled.addWidget(self.splitterMain)

        self.tabWidgetMain.addTab(self.tabInstalled, "")
        self.tabDiscover = QWidget()
        self.tabDiscover.setObjectName("tabDiscover")
        self.horizontalLayoutDiscover = QHBoxLayout(self.tabDiscover)
        self.horizontalLayoutDiscover.setSpacing(0)
        self.horizontalLayoutDiscover.setObjectName("horizontalLayoutDiscover")
        self.horizontalLayoutDiscover.setContentsMargins(0, 0, 0, 0)
        self.splitterDiscover = QSplitter(self.tabDiscover)
        self.splitterDiscover.setObjectName("splitterDiscover")
        self.splitterDiscover.setOrientation(Qt.Horizontal)
        self.widgetDiscoverLeft = QWidget(self.splitterDiscover)
        self.widgetDiscoverLeft.setObjectName("widgetDiscoverLeft")
        self.widgetDiscoverLeft.setMinimumSize(QSize(320, 0))
        self.verticalLayoutDiscoverLeft = QVBoxLayout(self.widgetDiscoverLeft)
        self.verticalLayoutDiscoverLeft.setSpacing(6)
        self.verticalLayoutDiscoverLeft.setObjectName("verticalLayoutDiscoverLeft")
        self.verticalLayoutDiscoverLeft.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayoutDiscoverSearch = QHBoxLayout()
        self.horizontalLayoutDiscoverSearch.setSpacing(6)
        self.horizontalLayoutDiscoverSearch.setObjectName(
            "horizontalLayoutDiscoverSearch"
        )
        self.horizontalLayoutDiscoverSearch.setContentsMargins(0, 0, 0, 0)
        self.lineEditDiscoverSearch = QLineEdit(self.widgetDiscoverLeft)
        self.lineEditDiscoverSearch.setObjectName("lineEditDiscoverSearch")
        self.lineEditDiscoverSearch.setClearButtonEnabled(True)

        self.horizontalLayoutDiscoverSearch.addWidget(self.lineEditDiscoverSearch)

        self.pushButtonDiscoverSearch = QPushButton(self.widgetDiscoverLeft)
        self.pushButtonDiscoverSearch.setObjectName("pushButtonDiscoverSearch")

        self.horizontalLayoutDiscoverSearch.addWidget(self.pushButtonDiscoverSearch)

        self.verticalLayoutDiscoverLeft.addLayout(self.horizontalLayoutDiscoverSearch)

        self.labelDiscoverStatus = QLabel(self.widgetDiscoverLeft)
        self.labelDiscoverStatus.setObjectName("labelDiscoverStatus")
        self.labelDiscoverStatus.setWordWrap(True)

        self.verticalLayoutDiscoverLeft.addWidget(self.labelDiscoverStatus)

        self.tableViewDiscover = QTableView(self.widgetDiscoverLeft)
        self.tableViewDiscover.setObjectName("tableViewDiscover")
        self.tableViewDiscover.setAlternatingRowColors(True)
        self.tableViewDiscover.setShowGrid(False)
        self.tableViewDiscover.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableViewDiscover.setSelectionMode(QAbstractItemView.SingleSelection)

        self.verticalLayoutDiscoverLeft.addWidget(self.tableViewDiscover)

        self.splitterDiscover.addWidget(self.widgetDiscoverLeft)
        self.widgetDiscoverRight = QWidget(self.splitterDiscover)
        self.widgetDiscoverRight.setObjectName("widgetDiscoverRight")
        sizePolicy.setHeightForWidth(
            self.widgetDiscoverRight.sizePolicy().hasHeightForWidth()
        )
        self.widgetDiscoverRight.setSizePolicy(sizePolicy)
        self.verticalLayoutDiscoverRight = QVBoxLayout(self.widgetDiscoverRight)
        self.verticalLayoutDiscoverRight.setSpacing(8)
        self.verticalLayoutDiscoverRight.setObjectName("verticalLayoutDiscoverRight")
        self.verticalLayoutDiscoverRight.setContentsMargins(0, 0, 0, 0)
        self.groupBoxDiscoverDetails = QGroupBox(self.widgetDiscoverRight)
        self.groupBoxDiscoverDetails.setObjectName("groupBoxDiscoverDetails")
        self.groupBoxDiscoverDetails.setMaximumSize(QSize(16777215, 240))
        self.formLayoutDiscoverDetails = QFormLayout(self.groupBoxDiscoverDetails)
        self.formLayoutDiscoverDetails.setObjectName("formLayoutDiscoverDetails")
        self.formLayoutDiscoverDetails.setFieldGrowthPolicy(
            QFormLayout.AllNonFixedFieldsGrow
        )
        self.formLayoutDiscoverDetails.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.formLayoutDiscoverDetails.setFormAlignment(Qt.AlignTop)
        self.formLayoutDiscoverDetails.setHorizontalSpacing(12)
        self.formLayoutDiscoverDetails.setVerticalSpacing(6)
        self.formLayoutDiscoverDetails.setContentsMargins(8, 8, 8, 8)
        self.labelDiscoverName = QLabel(self.groupBoxDiscoverDetails)
        self.labelDiscoverName.setObjectName("labelDiscoverName")

        self.formLayoutDiscoverDetails.setWidget(
            0, QFormLayout.ItemRole.LabelRole, self.labelDiscoverName
        )

        self.labelDiscoverNameValue = QLabel(self.groupBoxDiscoverDetails)
        self.labelDiscoverNameValue.setObjectName("labelDiscoverNameValue")
        self.labelDiscoverNameValue.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.formLayoutDiscoverDetails.setWidget(
            0, QFormLayout.ItemRole.FieldRole, self.labelDiscoverNameValue
        )

        self.labelDiscoverVersion = QLabel(self.groupBoxDiscoverDetails)
        self.labelDiscoverVersion.setObjectName("labelDiscoverVersion")

        self.formLayoutDiscoverDetails.setWidget(
            1, QFormLayout.ItemRole.LabelRole, self.labelDiscoverVersion
        )

        self.labelDiscoverVersionValue = QLabel(self.groupBoxDiscoverDetails)
        self.labelDiscoverVersionValue.setObjectName("labelDiscoverVersionValue")
        self.labelDiscoverVersionValue.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.formLayoutDiscoverDetails.setWidget(
            1, QFormLayout.ItemRole.FieldRole, self.labelDiscoverVersionValue
        )

        self.labelDiscoverSource = QLabel(self.groupBoxDiscoverDetails)
        self.labelDiscoverSource.setObjectName("labelDiscoverSource")

        self.formLayoutDiscoverDetails.setWidget(
            2, QFormLayout.ItemRole.LabelRole, self.labelDiscoverSource
        )

        self.labelDiscoverSourceValue = QLabel(self.groupBoxDiscoverDetails)
        self.labelDiscoverSourceValue.setObjectName("labelDiscoverSourceValue")
        self.labelDiscoverSourceValue.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.formLayoutDiscoverDetails.setWidget(
            2, QFormLayout.ItemRole.FieldRole, self.labelDiscoverSourceValue
        )

        self.labelDiscoverBinaries = QLabel(self.groupBoxDiscoverDetails)
        self.labelDiscoverBinaries.setObjectName("labelDiscoverBinaries")

        self.formLayoutDiscoverDetails.setWidget(
            3, QFormLayout.ItemRole.LabelRole, self.labelDiscoverBinaries
        )

        self.labelDiscoverBinariesValue = QLabel(self.groupBoxDiscoverDetails)
        self.labelDiscoverBinariesValue.setObjectName("labelDiscoverBinariesValue")
        self.labelDiscoverBinariesValue.setWordWrap(True)
        self.labelDiscoverBinariesValue.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        self.formLayoutDiscoverDetails.setWidget(
            3, QFormLayout.ItemRole.FieldRole, self.labelDiscoverBinariesValue
        )

        self.verticalLayoutDiscoverRight.addWidget(self.groupBoxDiscoverDetails)

        self.groupBoxDiscoverActions = QGroupBox(self.widgetDiscoverRight)
        self.groupBoxDiscoverActions.setObjectName("groupBoxDiscoverActions")
        self.horizontalLayoutDiscoverActions = QHBoxLayout(self.groupBoxDiscoverActions)
        self.horizontalLayoutDiscoverActions.setSpacing(8)
        self.horizontalLayoutDiscoverActions.setObjectName(
            "horizontalLayoutDiscoverActions"
        )
        self.horizontalLayoutDiscoverActions.setContentsMargins(8, 8, 8, 8)
        self.pushButtonInstall = QPushButton(self.groupBoxDiscoverActions)
        self.pushButtonInstall.setObjectName("pushButtonInstall")

        self.horizontalLayoutDiscoverActions.addWidget(self.pushButtonInstall)

        self.horizontalSpacerDiscoverActions = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayoutDiscoverActions.addItem(
            self.horizontalSpacerDiscoverActions
        )

        self.verticalLayoutDiscoverRight.addWidget(self.groupBoxDiscoverActions)

        self.verticalSpacerDiscover = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayoutDiscoverRight.addItem(self.verticalSpacerDiscover)

        self.splitterDiscover.addWidget(self.widgetDiscoverRight)

        self.horizontalLayoutDiscover.addWidget(self.splitterDiscover)

        self.tabWidgetMain.addTab(self.tabDiscover, "")
        self.splitterRoot.addWidget(self.tabWidgetMain)
        self.plainTextEditLog = QPlainTextEdit(self.splitterRoot)
        self.plainTextEditLog.setObjectName("plainTextEditLog")
        self.plainTextEditLog.setReadOnly(True)
        self.plainTextEditLog.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.plainTextEditLog.setMinimumSize(QSize(0, 140))
        font = QFont()
        font.setFamilies(["Consolas"])
        font.setPointSize(9)
        self.plainTextEditLog.setFont(font)
        self.splitterRoot.addWidget(self.plainTextEditLog)

        self.verticalLayoutMain.addWidget(self.splitterRoot)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 900, 33))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidgetMain.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "Scoop GUI", None)
        )
        self.lineEditSearch.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "Search", None)
        )
        self.groupBoxDetails.setTitle(
            QCoreApplication.translate("MainWindow", "Details", None)
        )
        self.labelName.setText(QCoreApplication.translate("MainWindow", "Name", None))
        self.labelNameValue.setText(QCoreApplication.translate("MainWindow", "-", None))
        self.labelVersion.setText(
            QCoreApplication.translate("MainWindow", "Version", None)
        )
        self.labelVersionValue.setText(
            QCoreApplication.translate("MainWindow", "-", None)
        )
        self.groupBoxActions.setTitle(
            QCoreApplication.translate("MainWindow", "Actions", None)
        )
        self.pushButtonRefresh.setText(
            QCoreApplication.translate("MainWindow", "Refresh", None)
        )
        self.pushButtonUninstall.setText(
            QCoreApplication.translate("MainWindow", "Uninstall", None)
        )
        self.pushButtonUpdate.setText(
            QCoreApplication.translate("MainWindow", "Update", None)
        )
        self.pushButtonCleanup.setText(
            QCoreApplication.translate("MainWindow", "Cleanup", None)
        )
        self.tabWidgetMain.setTabText(
            self.tabWidgetMain.indexOf(self.tabInstalled),
            QCoreApplication.translate("MainWindow", "Installed", None),
        )
        self.lineEditDiscoverSearch.setPlaceholderText(
            QCoreApplication.translate("MainWindow", "Search apps to install", None)
        )
        self.pushButtonDiscoverSearch.setText(
            QCoreApplication.translate("MainWindow", "Search", None)
        )
        self.labelDiscoverStatus.setText(
            QCoreApplication.translate(
                "MainWindow", "Type at least 2 characters, then click Search", None
            )
        )
        self.groupBoxDiscoverDetails.setTitle(
            QCoreApplication.translate("MainWindow", "Details", None)
        )
        self.labelDiscoverName.setText(
            QCoreApplication.translate("MainWindow", "Name", None)
        )
        self.labelDiscoverNameValue.setText(
            QCoreApplication.translate("MainWindow", "-", None)
        )
        self.labelDiscoverVersion.setText(
            QCoreApplication.translate("MainWindow", "Version", None)
        )
        self.labelDiscoverVersionValue.setText(
            QCoreApplication.translate("MainWindow", "-", None)
        )
        self.labelDiscoverSource.setText(
            QCoreApplication.translate("MainWindow", "Source", None)
        )
        self.labelDiscoverSourceValue.setText(
            QCoreApplication.translate("MainWindow", "-", None)
        )
        self.labelDiscoverBinaries.setText(
            QCoreApplication.translate("MainWindow", "Binaries", None)
        )
        self.labelDiscoverBinariesValue.setText(
            QCoreApplication.translate("MainWindow", "-", None)
        )
        self.groupBoxDiscoverActions.setTitle(
            QCoreApplication.translate("MainWindow", "Actions", None)
        )
        self.pushButtonInstall.setText(
            QCoreApplication.translate("MainWindow", "Install", None)
        )
        self.tabWidgetMain.setTabText(
            self.tabWidgetMain.indexOf(self.tabDiscover),
            QCoreApplication.translate("MainWindow", "Discover", None),
        )

    # retranslateUi
