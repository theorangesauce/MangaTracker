# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mangatracker-gui-edit.ui',
# licensing of 'mangatracker-gui-edit.ui' applies.
#
# Created: Fri Feb  7 10:11:07 2020
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_EditSeries(object):
    def setupUi(self, EditSeries):
        EditSeries.setObjectName("EditSeries")
        EditSeries.resize(431, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(EditSeries)
        self.verticalLayout.setObjectName("verticalLayout")
        self.edit_series_label = QtWidgets.QLabel(EditSeries)
        self.edit_series_label.setObjectName("edit_series_label")
        self.verticalLayout.addWidget(self.edit_series_label)
        self.edit_series_table = QtWidgets.QTableWidget(EditSeries)
        self.edit_series_table.setEditTriggers(QtWidgets.QAbstractItemView.DoubleClicked|QtWidgets.QAbstractItemView.SelectedClicked)
        self.edit_series_table.setColumnCount(2)
        self.edit_series_table.setObjectName("edit_series_table")
        self.edit_series_table.setColumnCount(2)
        self.edit_series_table.setRowCount(0)
        self.edit_series_table.horizontalHeader().setVisible(False)
        self.edit_series_table.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.edit_series_table)
        self.edit_series_button_layout = QtWidgets.QHBoxLayout()
        self.edit_series_button_layout.setObjectName("edit_series_button_layout")
        self.edit_series_save_button = QtWidgets.QPushButton(EditSeries)
        self.edit_series_save_button.setObjectName("edit_series_save_button")
        self.edit_series_button_layout.addWidget(self.edit_series_save_button)
        self.edit_series_cancel_button = QtWidgets.QPushButton(EditSeries)
        self.edit_series_cancel_button.setObjectName("edit_series_cancel_button")
        self.edit_series_button_layout.addWidget(self.edit_series_cancel_button)
        self.verticalLayout.addLayout(self.edit_series_button_layout)

        self.retranslateUi(EditSeries)
        QtCore.QMetaObject.connectSlotsByName(EditSeries)

    def retranslateUi(self, EditSeries):
        EditSeries.setWindowTitle(QtWidgets.QApplication.translate("EditSeries", "Edit Series", None, -1))
        self.edit_series_label.setText(QtWidgets.QApplication.translate("EditSeries", "Double-click a property to edit.", None, -1))
        self.edit_series_save_button.setText(QtWidgets.QApplication.translate("EditSeries", "Save", None, -1))
        self.edit_series_cancel_button.setText(QtWidgets.QApplication.translate("EditSeries", "Cancel", None, -1))

