#!/usr/bin/env python3
import sys
from PySide2.QtCore import Qt
from PySide2.QtWidgets import *
import ui_mainwindow
import ui_editseries
from databasemanager import DatabaseManager
from databasemanager import regexp
from series import Series
from series import SeriesItems as SI
from series import init_database
from config import Config
from mangatracker import entry_to_series

class MangaTrackerEditWindow(QWidget, ui_editseries.Ui_EditSeries):
    def __init__(self, rowid, parent=None):
        super(MangaTrackerEditWindow, self).__init__(parent)
        self.setupUi(self)
        self.edit_series_save_button.clicked.connect(self.save_edit)
        self.edit_series_cancel_button.clicked.connect(self.close)
        self.rowid = rowid
        data_mgr = DatabaseManager(Config().database_name, None)
        cur = data_mgr.query("SELECT rowid, * FROM Series WHERE rowid = %d"
                             % rowid)
        series = entry_to_series(cur.fetchone())
        self.table_setup(series)

    def save_edit(self):
        ### STUB
        self.close()
        
    def table_setup(self, series):
        headings = ["Name", "Alt. Names", "Author", "Volumes Owned",
                    "Next Volume", "Publisher", "Completed"]
        data = [series.name, series.alt_names, series.author,
                series.volumes_owned_readable, series.next_volume,
                series.publisher, "Yes" if series.is_completed else "No"]

        # Prepare table
        self.edit_series_table.clear()
        self.edit_series_table.setRowCount(len(headings))
        self.edit_series_table.setColumnCount(2)
        header = self.edit_series_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Populate table
        for i in range(len(headings)):
            headerItem = QTableWidgetItem(headings[i])
            dataItem = QTableWidgetItem(str(data[i]))
            headerItem.setFlags(headerItem.flags() & ~int(Qt.ItemIsEditable))
            self.edit_series_table.setItem(i, 0, headerItem)
            self.edit_series_table.setItem(i, 1, dataItem)

class MangaTrackerGUI(QMainWindow, ui_mainwindow.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MangaTrackerGUI, self).__init__(parent)
        self.setupUi(self)
        self.set_styles()
        self.list_series.currentItemChanged.connect(self.display_series)
        self.filter_series.textChanged.connect(self.filter_series_list)
        self.edit_series_button.clicked.connect(self.open_edit_window)

    def set_styles(self):
        self.list_series.setStyleSheet(
            "QListWidget::item {padding-top:8px;"
            "padding-bottom:8px; border:1px solid #5DA9F6;}"
            "QListWidget::item:selected{background:#5DA9F6;}")

    def open_edit_window(self):
        series_rowid = self.list_series.currentItem().data(Qt.UserRole)
        self.edit_window = MangaTrackerEditWindow(series_rowid)
        self.edit_window.show()        
        
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
