# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mangatracker-gui-add.ui',
# licensing of 'mangatracker-gui-add.ui' applies.
#
# Created: Mon Apr  6 16:15:37 2020
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_AddSeries(object):
    def setupUi(self, AddSeries):
        AddSeries.setObjectName("AddSeries")
        AddSeries.resize(431, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(AddSeries)
        self.verticalLayout.setObjectName("verticalLayout")
        self.add_series_label = QtWidgets.QLabel(AddSeries)
        self.add_series_label.setObjectName("add_series_label")
        self.verticalLayout.addWidget(self.add_series_label)
        self.add_series_table = QtWidgets.QTableWidget(AddSeries)
        self.add_series_table.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.SelectedClicked)
        self.add_series_table.setColumnCount(2)
        self.add_series_table.setObjectName("add_series_table")
        self.add_series_table.setColumnCount(2)
        self.add_series_table.setRowCount(0)
        self.add_series_table.horizontalHeader().setVisible(False)
        self.add_series_table.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.add_series_table)
        self.add_series_button_layout = QtWidgets.QHBoxLayout()
        self.add_series_button_layout.setObjectName("add_series_button_layout")
        self.add_series_add_button = QtWidgets.QPushButton(AddSeries)
        self.add_series_add_button.setObjectName("add_series_add_button")
        self.add_series_button_layout.addWidget(self.add_series_add_button)
        self.add_series_cancel_button = QtWidgets.QPushButton(AddSeries)
        self.add_series_cancel_button.setObjectName("add_series_cancel_button")
        self.add_series_button_layout.addWidget(self.add_series_cancel_button)
        self.verticalLayout.addLayout(self.add_series_button_layout)

        self.retranslateUi(AddSeries)
        QtCore.QMetaObject.connectSlotsByName(AddSeries)

    def retranslateUi(self, AddSeries):
        AddSeries.setWindowTitle(QtWidgets.QApplication.translate("AddSeries", "Add Series", None, -1))
        self.add_series_label.setText(QtWidgets.QApplication.translate("AddSeries", "Double-click a property to edit.", None, -1))
        self.add_series_add_button.setText(QtWidgets.QApplication.translate("AddSeries", "Add", None, -1))
        self.add_series_cancel_button.setText(QtWidgets.QApplication.translate("AddSeries", "Cancel", None, -1))

