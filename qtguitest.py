#!/usr/bin/env python3
import sys
from PySide2.QtCore import Qt
from PySide2.QtWidgets import *
import ui_mainwindow
from databasemanager import DatabaseManager
from databasemanager import regexp
from series import Series
from series import SeriesItems as SI
from series import init_database
from config import Config
from mangatracker import entry_to_series

class MangaTrackerGUI(QMainWindow, ui_mainwindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MangaTrackerGUI, self).__init__(parent)
        self.setupUi(self)
        self.set_styles()

    def set_styles(self):
        self.list_series.setStyleSheet(
            "QListWidget::item {padding-top:8px;"
            "padding-bottom:8px; border:1px solid #5DA9F6;}"
            "QListWidget::item:selected{background:#5DA9F6;}")

def get_list_items(data_mgr, mw, order="name"):
    cur = data_mgr.query("SELECT rowid, * FROM Series ORDER BY %s" % order)
    entries = cur.fetchall()
    unknown_entries = []
    count = 0
    config = Config()
    for entry in entries:
        if entry[SI[order.upper()]] == "Unknown":
            unknown_entries.append(entry)
            continue
        series = entry_to_series(entry)
        series_item = QListWidgetItem(series.compact_string())
        series_item.setData(Qt.UserRole, series.rowid)
        mw.list_series.addItem(series_item)
        
def gui_main():
    config = Config()
    data_mgr = DatabaseManager(config.database_name, init_database)

    app = QApplication(sys.argv)
    main_window = MangaTrackerGUI()
    get_list_items(data_mgr, main_window)
    main_window.show()
    app.exec_()

if __name__ == "__main__":
    gui_main()
