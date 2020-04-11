#!/usr/bin/env python3
import sys
from PySide2.QtCore import Qt
from PySide2.QtWidgets import *
import ui_mainwindow
import ui_editseries
import ui_addseries
from databasemanager import DatabaseManager
from databasemanager import regexp
from series import Series
from series import SeriesItems as SI
from series import init_database
from series import generate_volumes_owned
from config import Config
from mangatracker import entry_to_series

class MangaTrackerAddWindow(QDialog, ui_addseries.Ui_AddSeries):
    def __init__(self, parent=None):
        super(MangaTrackerAddWindow, self).__init__(parent)
        self.setupUi(self)
        self.table_setup()
        self.add_series_add_button.clicked.connect(self.add_series)
        self.add_series_cancel_button.clicked.connect(self.close)

    def validate_cells(self, item):
        if item.row() == 0: # Name
            name = item.text()
            data_mgr = DatabaseManager(Config().database_name, None)
            cur = data_mgr.query("SELECT name FROM Series WHERE name = '{0}'"
                                 .format(name.replace("'", "''")))
            row = cur.fetchall()
            if row or name in ["", "Unknown"]:
                item.setBackground(Qt.red)                
            else:
                item.setBackground(Qt.white)
                
        elif item.row() == 3: # Volumes Owned
            volumes_owned_raw = item.text()
            pattern = "\d+(-\d+)?(,\s*\d+(-\d+)?)*\s*$"
            print(regexp(pattern, volumes_owned_raw))
            if not regexp(pattern, volumes_owned_raw):
                item.setBackground(Qt.red)
            else:
                item.setBackground(Qt.white)

    def add_series(self):
        for i in range(self.add_series_table.rowCount()):
            if self.add_series_table.item(i, 1).background() == Qt.red:
                return

        name = self.add_series_table.item(0, 1).text()
        if name in ["", "Unknown"]:
            self.add_series_table.item(0, 1).setBackground(Qt.red)
            return

        alt_names = self.add_series_table.item(1, 1).text()
        author = self.add_series_table.item(2, 1).text()
        volumes_owned = generate_volumes_owned(
            self.add_series_table.item(3, 1).text())
        publisher = self.add_series_table.item(4, 1).text()
        is_completed = 1 if self.add_series_table.cellWidget(5, 1).currentText == "Yes" else 0
        
        new_series = Series(name=name,
                            volumes_owned=volumes_owned,
                            is_completed=is_completed,
                            next_volume=-1,
                            publisher=publisher,
                            author=author,
                            alt_names=alt_names)

        if new_series.add_series_to_database(data_mgr):
            self.close()
        
    def table_setup(self):
        """Generates table elements for creation of a new series.

        Clears any existing elements in the table, then generates a
        two-column table, with headings in the first column and space
        for series info in the second. The first column is not
        editable, and the second column is editable. By default, only
        two fields are filled in when the table is completed: 'Name'
        and 'Completed'.

        """
        headings = ["Name", "Alt. Names", "Author", "Volumes Owned",
                    "Publisher", "Completed"]
        data = ["Unknown", "", "", "", "", "No"]

        # Prepare table
        self.add_series_table.clear()
        self.add_series_table.setRowCount(len(headings))
        self.add_series_table.setColumnCount(2)
        header = self.add_series_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Populate table
        for i in range(len(headings)):
            headerItem = QTableWidgetItem(headings[i])
            headerItem.setFlags(headerItem.flags() & ~int(Qt.ItemIsEditable))
            self.add_series_table.setItem(i, 0, headerItem)
            
            if headings[i] == "Completed":
                dataItem = QComboBox()
                dataItem.insertItem(0, "No")
                dataItem.insertItem(1, "Yes")
                if str(data[i]) == "No":
                    dataItem.setCurrentIndex(0)
                else:
                    dataItem.setCurrentIndex(1)
                self.add_series_table.setCellWidget(i, 1, dataItem)
            else:
                dataItem = QTableWidgetItem(str(data[i]))
                self.add_series_table.setItem(i, 1, dataItem)


        self.add_series_table.itemChanged.connect(self.validate_cells)


class MangaTrackerEditWindow(QDialog, ui_editseries.Ui_EditSeries):
    """Series editing window for Mangatracker GUI interface.

    Displays a user-editable table containing series properties, which
    can be edited and saved using a button at the bottom of the
    window.

    """
    def __init__(self, rowid, parent=None):
        """Initializes edit window

        Retrieves series information from database and populates the
        table with the results for the user to edit.

        """
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
        """Saves changes to series object or discards them depending on user choice.

        Displays a dialog to the user asking if they want to save. If
        'save' is selected, all modified properties of the series are
        saved to the database and the edit window closes. If 'discard'
        is selected, the window closes without saving any changes. If
        'cancel' is selected, the dialog is closed and editing can
        continue.

        """
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
                try:
                    new_data = self.edit_series_table.item(i, 1).text()
                except AttributeError:
                    new_data = self.edit_series_table.cellWidget(i, 1).currentText()

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
        """Generates table elements based on series.

        Clears any existing elements in the table, then uses series to
        generate a two-column table, with headings in the first column
        and data in the second. The first column is not editable,
        and the second column is editable.

        """
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
            headerItem.setFlags(headerItem.flags() & ~int(Qt.ItemIsEditable))
            self.edit_series_table.setItem(i, 0, headerItem)
            
            if headings[i] == "Completed":
                dataItem = QComboBox()
                dataItem.insertItem(0, "No")
                dataItem.insertItem(1, "Yes")
                if str(data[i]) == "No":
                    dataItem.setCurrentIndex(0)
                else:
                    dataItem.setCurrentIndex(1)
                self.edit_series_table.setCellWidget(i, 1, dataItem)
            else:
                dataItem = QTableWidgetItem(str(data[i]))
                if headings[i] == "Next Volume":
                    dataItem.setFlags(dataItem.flags() & ~int(Qt.ItemIsEditable))
                self.edit_series_table.setItem(i, 1, dataItem)


class MangaTrackerGUI(QMainWindow, ui_mainwindow.Ui_MainWindow):
    """Main window for the MangaTracker GUI interface. 

    Contains a list of all series in the database on the left, and a
    table on the right to show the currently selected series. A user
    can filter the list using a search bar directly above the list. A
    user can add a series, remove a series, change settings, edit a
    series, add the next volume for a series, or mark a series as
    completed using buttons at the bottom of the window.

    """
    def __init__(self, parent=None):
        """Creates main window, links buttons and filter bar to functions."""
        super(MangaTrackerGUI, self).__init__(parent)
        self.setupUi(self)
        self.set_styles()
        self.get_list_items()
        self.list_series.currentItemChanged.connect(self.display_series)
        self.filter_series.textChanged.connect(self.filter_series_list)
        self.edit_series_button.clicked.connect(self.open_edit_window)
        self.add_series_button.clicked.connect(self.open_add_window)

    def set_styles(self):
        """Sets styling for list items."""
        self.list_series.setStyleSheet(
            "QListWidget::item {padding-top:8px;"
            "padding-bottom:8px; border:1px solid #5DA9F6;}"
            "QListWidget::item:selected{background:#5DA9F6;}")

    def open_add_window(self):
        self.add_window = MangaTrackerAddWindow()
        self.add_window.setWindowModality(Qt.ApplicationModal)
        self.add_window.finished.connect(self.get_list_items)
        self.add_window.show()
        
    def open_edit_window(self):
        """Opens edit window for selected series.

        Retrieves the unique rowid for the selected series, and
        initializes the MangaTrackerEditWindow() class. Triggers
        display_series() when edit window is closed.

        """
        series_rowid = self.list_series.currentItem().data(Qt.UserRole)
        self.edit_window = MangaTrackerEditWindow(series_rowid)
        self.edit_window.setWindowModality(Qt.ApplicationModal)
        self.edit_window.finished.connect(self.display_series)
        self.edit_window.show()
        
    def table_setup(self, series):
        """Generates table elements based on series.

        Clears any existing elements in the table, then uses series to
        generate a two-column table, with headings in the first column
        and data in the second.

        """
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
        """Retrieves and displays info for selected series.

        This function retrieves the unique rowid for the selected
        series and retrieves the series from the database. It then
        updates all main window elements which show series info to
        show up-to-date properties. Once all series information is
        properly displayed, buttons which can change the selected
        series's properties are enabled.

        """
        data_mgr = DatabaseManager(Config().database_name, None)
        if self.list_series.currentItem():
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
        """Hides list elements whose text does not contain a user-provided string.
        
        When the text in the filter bar above the list is edited, this
        function takes the updated text and compares it to each
        element of the list. If the series string in the list element
        does not contain the updated text, the element will be
        hidden. As a result, the filter only works on name, author,
        and 'Completed'; functionality for filtering by other
        properties is planned for future updates.

        """
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

    def get_list_items(self, order="name"):
        """Retrieves all series from database and populates list in main window.

        Populates the list in the main window with the compact_string()
        representations of all the series in the database, sorting by the
        given property (default "name") and placing any series with an
        unknown value for that property at the end of the list

        """
        if not order:
            order = "name"
        data_mgr = DatabaseManager(Config().database_name, None)
        cur = data_mgr.query("SELECT rowid, * FROM Series ORDER BY %s" % order)
        entries = cur.fetchall()
        unknown_entries = []
        count = 0
        config = Config()
        selected_series = None

        if self.list_series.currentItem():
            selected_series = self.list_series.currentItem().data(Qt.UserRole)
        self.list_series.clear()
        for entry in entries:
            if entry[SI[order.upper()]] == "Unknown":
                unknown_entries.append(entry)
                continue
            series = entry_to_series(entry)
            series_item = QListWidgetItem(series.compact_string())
            series_item.setData(Qt.UserRole, series.rowid)
            self.list_series.addItem(series_item)
            if selected_series and selected_series == series.rowid:
                self.list_series.setCurrentItem(series_item)
        for entry in unknown_entries:
            series = entry_to_series(entry)
            series_item = QListWidgetItem(series.compact_string())
            series_item.setData(Qt.UserRole, series.rowid)
            self.list_series.addItem(series_item)
            if selected_series and selected_series == series.rowid:
                self.list_series.setCurrentItem(series_item)
        
def gui_main():
    """Starts the main window for MangaTracker GUI"""
    config = Config()
    data_mgr = DatabaseManager(config.database_name, init_database)
    app = QApplication(sys.argv)
    main_window = MangaTrackerGUI()

    main_window.show()
    app.exec_()

if __name__ == "__main__":
    gui_main()
