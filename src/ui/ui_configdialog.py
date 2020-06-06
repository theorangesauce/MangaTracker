# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xml/mangatracker-gui-config.ui',
# licensing of 'xml/mangatracker-gui-config.ui' applies.
#
# Created: Fri May  8 14:57:20 2020
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_ConfigDialog(object):
    def setupUi(self, ConfigDialog):
        ConfigDialog.setObjectName("ConfigDialog")
        ConfigDialog.resize(400, 119)
        self.gridLayout = QtWidgets.QGridLayout(ConfigDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.database_name_label = QtWidgets.QLabel(ConfigDialog)
        self.database_name_label.setObjectName("database_name_label")
        self.gridLayout.addWidget(self.database_name_label, 0, 0, 1, 1)
        self.database_name_text = QtWidgets.QLineEdit(ConfigDialog)
        self.database_name_text.setObjectName("database_name_text")
        self.gridLayout.addWidget(self.database_name_text, 0, 1, 1, 1)
        self.show_empty_series_label = QtWidgets.QLabel(ConfigDialog)
        self.show_empty_series_label.setObjectName("show_empty_series_label")
        self.gridLayout.addWidget(self.show_empty_series_label, 1, 0, 1, 1)
        self.show_empty_series_buttons = QtWidgets.QHBoxLayout()
        self.show_empty_series_buttons.setObjectName("show_empty_series_buttons")
        self.show_empty_series_yes_button = QtWidgets.QRadioButton(ConfigDialog)
        self.show_empty_series_yes_button.setObjectName("show_empty_series_yes_button")
        self.show_empty_series_buttons.addWidget(self.show_empty_series_yes_button)
        self.show_empty_series_no_button = QtWidgets.QRadioButton(ConfigDialog)
        self.show_empty_series_no_button.setChecked(True)
        self.show_empty_series_no_button.setObjectName("show_empty_series_no_button")
        self.show_empty_series_buttons.addWidget(self.show_empty_series_no_button)
        self.gridLayout.addLayout(self.show_empty_series_buttons, 1, 1, 1, 1)
        self.default_to_gui_label = QtWidgets.QLabel(ConfigDialog)
        self.default_to_gui_label.setObjectName("default_to_gui_label")
        self.gridLayout.addWidget(self.default_to_gui_label, 2, 0, 1, 1)
        self.default_to_gui_buttons = QtWidgets.QHBoxLayout()
        self.default_to_gui_buttons.setObjectName("default_to_gui_buttons")
        self.default_to_gui_yes_button = QtWidgets.QRadioButton(ConfigDialog)
        self.default_to_gui_yes_button.setChecked(True)
        self.default_to_gui_yes_button.setObjectName("default_to_gui_yes_button")
        self.default_to_gui_buttons.addWidget(self.default_to_gui_yes_button)
        self.default_to_gui_no_button = QtWidgets.QRadioButton(ConfigDialog)
        self.default_to_gui_no_button.setObjectName("default_to_gui_no_button")
        self.default_to_gui_buttons.addWidget(self.default_to_gui_no_button)
        self.gridLayout.addLayout(self.default_to_gui_buttons, 2, 1, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.config_save = QtWidgets.QPushButton(ConfigDialog)
        self.config_save.setObjectName("config_save")
        self.horizontalLayout_4.addWidget(self.config_save)
        self.config_cancel = QtWidgets.QPushButton(ConfigDialog)
        self.config_cancel.setObjectName("config_cancel")
        self.horizontalLayout_4.addWidget(self.config_cancel)
        self.gridLayout.addLayout(self.horizontalLayout_4, 3, 0, 1, 2)

        self.retranslateUi(ConfigDialog)
        QtCore.QMetaObject.connectSlotsByName(ConfigDialog)

    def retranslateUi(self, ConfigDialog):
        ConfigDialog.setWindowTitle(QtWidgets.QApplication.translate("ConfigDialog", "Config", None, -1))
        self.database_name_label.setText(QtWidgets.QApplication.translate("ConfigDialog", "Database Name", None, -1))
        self.database_name_text.setText(QtWidgets.QApplication.translate("ConfigDialog", "manga.db", None, -1))
        self.show_empty_series_label.setText(QtWidgets.QApplication.translate("ConfigDialog", "Show Empty Series in Lists", None, -1))
        self.show_empty_series_yes_button.setText(QtWidgets.QApplication.translate("ConfigDialog", "Yes", None, -1))
        self.show_empty_series_no_button.setText(QtWidgets.QApplication.translate("ConfigDialog", "No", None, -1))
        self.default_to_gui_label.setText(QtWidgets.QApplication.translate("ConfigDialog", "Open GUI by default?", None, -1))
        self.default_to_gui_yes_button.setText(QtWidgets.QApplication.translate("ConfigDialog", "Yes", None, -1))
        self.default_to_gui_no_button.setText(QtWidgets.QApplication.translate("ConfigDialog", "No", None, -1))
        self.config_save.setText(QtWidgets.QApplication.translate("ConfigDialog", "Save", None, -1))
        self.config_cancel.setText(QtWidgets.QApplication.translate("ConfigDialog", "Cancel", None, -1))

