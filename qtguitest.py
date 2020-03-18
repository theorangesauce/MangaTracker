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
from series import generate_volumes_owned
from config import Config
from mangatracker import entry_to_series

class MangaTrackerEditWindow(QDialog, ui_editseries.Ui_EditSeries):
    def __init__(self, rowid, parent=None):
        super(MangaTrackerEditWindow, self).__init__(parent)
        self.setupUi(self)
        self.edit_series_save_button.clicked.connect(self.save_edit)
        self.edit_series_cancel_button.clicked.connect(self.close)
        self.rowid = rowid
        data_mgr = DatabaseManager(Config().database_name, None)
        cur = data_mgr.query("SELECT rowid, * FROM Series WHERE rowid = %d"
                             % rowid)
        self.series = entry_to_series(cur.fetchone())
        self.table_setup(self.series)

    def save_edit(self):
        ### STUB
        reserved_words = ["unknown"]
        confirm_dialog = QMessageBox.question(
            self, "Save Changes",
            "Are you sure you want to save changes?\nThis cannot be undone.",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Cancel)

        if confirm_dialog == QMessageBox.Save:
            series_keys = ["name", "alt_names", "author",
                           "volumes_owned", "next_volume",
                           "publisher", "is_completed"]
            data_mgr = DatabaseManager(Config().database_name, None)

            for i in range(len(series_keys)):
                new_data = self.edit_series_table.item(i, 1).text()
                if series_keys[i] == "name":
                    if new_data and self.series.name != new_data:
                        cur = data_mgr.query("SELECT name FROM Series WHERE "
                                             "name = '{0}'"
                                             .format(new_data
                                                     .replace("'", "''")))
                        row = cur.fetchall()
                        if not row:
                            self.series.name = new_data
                            
                elif series_keys[i] == "volumes_owned":
                    new_data = generate_volumes_owned(new_data)
                    self.series.volumes_owned = new_data
                    self.series.vol_arr = [int(x) for x in
                                           self.series.volumes_owned.split(',')]
                    
                elif series_keys[i] == "next_volume":
                    self.series.next_volume = self.series.calculate_next_volume()
                    
                elif series_keys[i] == "is_completed":
                    if new_data in ["Yes", "yes", "Y", "y", 1]:
                        self.series.is_completed = 1
                    elif new_data in ["No", "no", "N", "n", 0]:
                        self.series.is_completed = 0

                else:
                    self.series.__dict__[series_keys[i]] = new_data

            self.series.update_database_entry(data_mgr)
            self.close()
        elif confirm_dialog == QMessageBox.Discard:
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
        self.edit_window.setWindowModality(Qt.ApplicationModal)
        self.edit_window.finished.connect(self.display_series)
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
            dataItem = QTableWidgetItem(str(data[i]))
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

        self.list_series.currentItem().setText(series.compact_string())
        self.table_setup(series)
        self.edit_series_button.setEnabled(True)
        self.remove_series_button.setEnabled(True)
        self.add_next_volume_button.setEnabled(True)
        self.mark_as_completed_button.setEnabled(True)

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
