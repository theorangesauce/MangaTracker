# DatabaseManager.py
# SQLite3 Database Manager for Series objects

import sqlite3 as lite
import re

# TODO: Create an author table and a publisher table
class DatabaseManager(object):
    """
    DatabaseManager(object)
    Main interface between program and SQLite3 database
    """
    def __init__(self, database_name, new_db_needed=True):
        """
        __init__(self, database_name, boolean)
        Set up a manager for the database, loading from a file or
        creating a new database if one does not exist
        """
        self.con = lite.connect(database_name)
        self.con.create_function("REGEXP", 2, regexp)
        self.cur = self.con.cursor()

        self.query("SELECT name FROM sqlite_master "\
                   "WHERE type='table' AND name='Series'")

        if self.cur.fetchone() == None:
            self.query("CREATE TABLE Series(name TEXT, volumes_owned TEXT, "
                       "is_completed INT, next_volume INT, publisher TEXT, "
                       "author TEXT, alt_names TEXT, PRIMARY KEY(name))")
            if new_db_needed:
                next_series = input_series(self)
                while next_series != None:
                    if next_series.add_series_to_database(self):
                        print(next_series)
                    else:
                        print("Failed to add series! (name conflict)")
                    next_series = input_series(self)

    def query(self, arg):
        """Runs a query on the database and returns the result"""
        self.cur.execute(arg)
        self.con.commit()
        return self.cur

    def __del__(self):
        """Close connection to database when object goes out of scope"""
        self.con.close()

def regexp(pattern, value):
    """
    regexp()
    Simple regex function to add to SQLite instance

    Arguments:
    pattern - regex to filter with
    value   - string to search with regex
    """
    reg = re.compile(pattern)
    return reg.search(value) is not None
