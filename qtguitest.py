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
        self.list_series.currentItemChanged.connect(self.display_series)
        self.filter_series.textChanged.connect(self.filter_series_list)

    def set_styles(self):
        self.list_series.setStyleSheet(
            "QListWidget::item {padding-top:8px;"
            "padding-bottom:8px; border:1px solid #5DA9F6;}"
            "QListWidget::item:selected{background:#5DA9F6;}")

    def table_setup(self, series):
        headings = ["Name", "Alt. Names", "Author", "Volumes Owned",
                    "Next Volume", "Publisher", "Completed"]
        data = [series.name, series.alt_names, series.author,
                series.volumes_owned_readable, series.next_volume,
                series.publisher, "Yes" if series.is_completed else "No"]

        # Prepare table
        self.series_info_display.clear()
        self.series_info_display.setRowCount(len(headings))
        self.series_info_display.setColumnCount(2)
        header = self.series_info_display.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Populate table
        for i in range(len(headings)):
            headerItem = QTableWidgetItem(headings[i])
            dataItem = QTableWidgetItem(data[i])
            self.series_info_display.setItem(i, 0, headerItem)
            self.series_info_display.setItem(i, 1, dataItem)
            

    def display_series(self):
        # DEBUG
        # print(self.list_series.currentItem().data(Qt.UserRole))
        data_mgr = DatabaseManager(Config().database_name, None)
        series_rowid = self.list_series.currentItem().data(Qt.UserRole)
        cur = data_mgr.query("SELECT rowid, * FROM Series WHERE rowid = %d"
                             % series_rowid)
        series = entry_to_series(cur.fetchone())
        self.table_setup(series)

    def filter_series_list(self):
        filter_text = self.filter_series.text()
        # If empty string, make sure all items are visible
        if not filter_text:
            for i in range(self.list_series.count()):
                self.list_series.item(i).setHidden(False)
            return
        
        matches = self.list_series.findItems(filter_text, Qt.MatchContains)

        ### Can't use this because 'if item in matches' throws
        ### 'Operator not implemented' error
        # for i in range(self.list_series.count()):
        #     item = self.list_series.item(i)
        #     print(item)
        #     if item in matches:
        #         item.setHidden(False)
        #     else:
        #         item.setHidden(True)
        
        # Hide all items, then show items which match filter  
        for i in range(self.list_series.count()):
            self.list_series.item(i).setHidden(True)
        for i in matches:
            i.setHidden(False)
        
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
    for entry in unknown_entries:
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
