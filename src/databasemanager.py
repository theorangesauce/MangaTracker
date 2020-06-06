""" databasemanager.py
SQLite3 Database Manager for Series objects

Copyright 2019 by Nicholas Bishop
"""
import sqlite3 as lite
import re


# TODO: Create an author table and a publisher table
class DatabaseManager():
    """
    DatabaseManager(object)
    Main interface between program and SQLite3 database
    """
    def __init__(self, database_name, init_database, new_db_needed=True):
        """
        __init__(self, database_name, init_database, boolean)
        Set up a manager for the database, loading from a file or
        creating a new database if one does not exist. Once
        database is created, the program calls a specialized
        function to initialize the database, if present.
        """
        self.con = lite.connect(database_name)
        self.con.create_function("REGEXP", 2, regexp)
        self.cur = self.con.cursor()

        if init_database is not None:
            init_database(self, new_db_needed)

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


def is_database(filename):
    """Verify that file filename is a SQLite database.

    A file is considered a valid database if:
     - the filename ends in .db, and
     - executing pragma schema_version returns a value >= 0
    """
    if filename[-3:] != ".db":
        return False
    try:
        con = lite.connect(filename)
        if con.cursor().execute("pragma schema_version").fetchone()[0] >= 0:
            con.close()
            return True

        con.close()
        return False

    except lite.DatabaseError:
        return False
