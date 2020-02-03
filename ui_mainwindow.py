# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mangatracker-gui.ui',
# licensing of 'mangatracker-gui.ui' applies.
#
# Created: Mon Feb  3 14:35:27 2020
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(710, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.main_window_container = QtWidgets.QHBoxLayout()
        self.main_window_container.setObjectName("main_window_container")
        self.left_column_container = QtWidgets.QVBoxLayout()
        self.left_column_container.setObjectName("left_column_container")
        self.filter_series = QtWidgets.QLineEdit(self.centralwidget)
        self.filter_series.setObjectName("filter_series")
        self.left_column_container.addWidget(self.filter_series)
        self.list_series = QtWidgets.QListWidget(self.centralwidget)
        self.list_series.setObjectName("list_series")
        self.left_column_container.addWidget(self.list_series)
        self.left_button_container = QtWidgets.QHBoxLayout()
        self.left_button_container.setObjectName("left_button_container")
        self.settings_button = QtWidgets.QPushButton(self.centralwidget)
        self.settings_button.setObjectName("settings_button")
        self.left_button_container.addWidget(self.settings_button)
        self.add_series_button = QtWidgets.QPushButton(self.centralwidget)
        self.add_series_button.setObjectName("add_series_button")
        self.left_button_container.addWidget(self.add_series_button)
        self.left_column_container.addLayout(self.left_button_container)
        self.main_window_container.addLayout(self.left_column_container)
        self.right_column_container = QtWidgets.QVBoxLayout()
        self.right_column_container.setObjectName("right_column_container")
        self.series_info_display = QtWidgets.QTableWidget(self.centralwidget)
        self.series_info_display.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.series_info_display.setColumnCount(2)
        self.series_info_display.setObjectName("series_info_display")
        self.series_info_display.setColumnCount(2)
        self.series_info_display.setRowCount(0)
        self.series_info_display.horizontalHeader().setVisible(False)
        self.series_info_display.verticalHeader().setVisible(False)
        self.right_column_container.addWidget(self.series_info_display)
        self.right_button_container = QtWidgets.QGridLayout()
        self.right_button_container.setObjectName("right_button_container")
        self.edit_series_button = QtWidgets.QPushButton(self.centralwidget)
        self.edit_series_button.setObjectName("edit_series_button")
        self.right_button_container.addWidget(self.edit_series_button, 0, 0, 1, 1)
        self.remove_series_button = QtWidgets.QPushButton(self.centralwidget)
        self.remove_series_button.setObjectName("remove_series_button")
        self.right_button_container.addWidget(self.remove_series_button, 0, 1, 1, 1)
        self.add_next_volume_button = QtWidgets.QPushButton(self.centralwidget)
        self.add_next_volume_button.setObjectName("add_next_volume_button")
        self.right_button_container.addWidget(self.add_next_volume_button, 1, 0, 1, 1)
        self.mark_as_completed_button = QtWidgets.QPushButton(self.centralwidget)
        self.mark_as_completed_button.setObjectName("mark_as_completed_button")
        self.right_button_container.addWidget(self.mark_as_completed_button, 1, 1, 1, 1)
        self.right_column_container.addLayout(self.right_button_container)
        self.main_window_container.addLayout(self.right_column_container)
        self.horizontalLayout_3.addLayout(self.main_window_container)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtWidgets.QApplication.translate("MainWindow", "MainWindow", None, -1))
        self.filter_series.setPlaceholderText(QtWidgets.QApplication.translate("MainWindow", "Filter", None, -1))
        self.settings_button.setText(QtWidgets.QApplication.translate("MainWindow", "Settings", None, -1))
        self.add_series_button.setText(QtWidgets.QApplication.translate("MainWindow", "Add", None, -1))
        self.edit_series_button.setText(QtWidgets.QApplication.translate("MainWindow", "Edit", None, -1))
        self.remove_series_button.setText(QtWidgets.QApplication.translate("MainWindow", "Remove", None, -1))
        self.add_next_volume_button.setText(QtWidgets.QApplication.translate("MainWindow", "Add Next Volume", None, -1))
        self.mark_as_completed_button.setText(QtWidgets.QApplication.translate("MainWindow", "Mark as Completed", None, -1))

