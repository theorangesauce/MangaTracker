# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mangatracker-gui-config.ui',
# licensing of 'mangatracker-gui-config.ui' applies.
#
# Created: Sun Apr 19 19:13:02 2020
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_ConfigDialog(object):
    def setupUi(self, ConfigDialog):
        ConfigDialog.setObjectName("ConfigDialog")
        ConfigDialog.resize(400, 113)
        self.verticalLayout = QtWidgets.QVBoxLayout(ConfigDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.database_name_label = QtWidgets.QLabel(ConfigDialog)
        self.database_name_label.setObjectName("database_name_label")
        self.horizontalLayout_3.addWidget(self.database_name_label)
        self.database_name_text = QtWidgets.QLineEdit(ConfigDialog)
        self.database_name_text.setObjectName("database_name_text")
        self.horizontalLayout_3.addWidget(self.database_name_text)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.config_save = QtWidgets.QPushButton(ConfigDialog)
        self.config_save.setObjectName("config_save")
        self.horizontalLayout_4.addWidget(self.config_save)
        self.config_cancel = QtWidgets.QPushButton(ConfigDialog)
        self.config_cancel.setObjectName("config_cancel")
        self.horizontalLayout_4.addWidget(self.config_cancel)
        self.verticalLayout.addLayout(self.horizontalLayout_4)

        self.retranslateUi(ConfigDialog)
        QtCore.QMetaObject.connectSlotsByName(ConfigDialog)

    def retranslateUi(self, ConfigDialog):
        ConfigDialog.setWindowTitle(QtWidgets.QApplication.translate("ConfigDialog", "Config", None, -1))
        self.database_name_label.setText(QtWidgets.QApplication.translate("ConfigDialog", "Database Name", None, -1))
        self.database_name_text.setText(QtWidgets.QApplication.translate("ConfigDialog", "manga.db", None, -1))
        self.config_save.setText(QtWidgets.QApplication.translate("ConfigDialog", "Save", None, -1))
        self.config_cancel.setText(QtWidgets.QApplication.translate("ConfigDialog", "Cancel", None, -1))

