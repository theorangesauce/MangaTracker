""" series.py
Container for information regarding a manga series

Copyright 2019 by Nicholas Bishop
"""

import math
from enum import IntEnum
from config import Config

class SeriesItems(IntEnum):
    """
    SeriesItems(IntEnum)

    An enum tracking the database column numbers for each series
    property, when selected using 'SELECT rowid, * FROM Series'. Allows
    for column order to change while keeping changes local to series.py.
    """
    ROWID = 0
    NAME = 1
    VOL_OWNED = 2
    IS_COMPLETED = 3
    NEXT_VOLUME = 4
    PUBLISHER = 5
    AUTHOR = 6
    ALT_NAMES = 7

class Series():
    """
    Series()

    A single manga series. Contains the name of the series, the number of
    volumes currently owned, whether the series is completed
    """
    def __init__(self, **kwargs):
        """
        __init__(self, args)
        Create a series object

        Keyword Arguments:
        name (String) -- Name of series
        volumes_owned (String) -- Comma-separated values representing
            volumes in collection
        is_completed (Int) -- whether all volumes owned or not
        next_volume -- Lowest-numbered volume not currently owned; set by
            get_next_volume() (default -1)
        publisher -- Publisher for series (default 'Unknown')
        author -- Author for series
        alt_names -- Alternate names for series (ex. in other languages)
            (default to empty string)
        rowid -- Row ID in database to use for updates (default None)
        volume_limit -- The current maximum number of volumes tracked
            per series
        compact_list -- A boolean deciding whether __str__ should return
            a single line or multiple lines.
        """
        valid_keys = ["name", "volumes_owned", "is_completed",
                      "next_volume", "publisher", "author",
                      "alt_names", "rowid"]

        for key in valid_keys:
            self.__dict__[key] = kwargs.get(key)

        # self.name = str(name)
        # self.volumes_owned = str(volumes_owned)
        # self.is_completed = is_completed
        # self.next_volume = next_volume
        # self.publisher = str(publisher)
        # self.author = str(author)
        # self.alt_names = str(alt_names)
        # self.rowid = rowid

        self.vol_arr = [int(x) for x in self.volumes_owned.split(',')]
        self.volumes_owned_readable = ""
        self.get_volumes_owned()
        if self.next_volume == -1 or not self.next_volume:
            self.next_volume = self.calculate_next_volume()

    def get_volumes_owned(self):
        """
        get_volumes_owned()
        Inverse of generate function; convert integers into human-readable
        format (same as original input format)
        """
        if self.volumes_owned_readable == "":
            index = 0
            first = -1
            last = -1
            none_owned = 1

            for num in self.vol_arr:
                if num == 0: # no volumes in set of 32, no need to check bits
                    if first != -1:
                        last = index * 32
                        self.volumes_owned_readable += (
                            "{0}, ".format(first) if first == last
                            else "{0}-{1}, ".format(first, last))
                        first = -1
                    index += 1
                    continue

                none_owned = 0
                for i in range(0, 32):
                    # assuming sequential
                    if first == -1 and num & (1 << i) != 0:
                        first = index * 32 + i + 1

                    if first != -1 and num & (1 << i) == 0:
                        last = index * 32 + i
                        self.volumes_owned_readable += (
                            "{0}, ".format(first) if first == last
                            else "{0}-{1}, ".format(first, last))
                        first = -1
                index += 1

            if first != -1: # last set of volumes reaches volume limit
                last = Config().volume_limit
                self.volumes_owned_readable += (
                    "{0}, ".format(first) if first == last
                    else "{0}-{1}, ".format(first, last))
                first = -1
            if none_owned:
                self.volumes_owned_readable = "None"
            else:
                self.volumes_owned_readable = self.volumes_owned_readable[:-2]
        return self.volumes_owned_readable

    def get_is_completed(self):
        """Returns whether all volumes for series are in collection"""
        return "Yes" if self.is_completed == 1 else "No"

    def get_volumes_owned_binary(self):
        """Converts vol_arr to a single binary string listing all volumes"""
        vol_str = ""
        for val in self.vol_arr:
            vol_str += "{0:032b}".format(val)[::-1]
        return vol_str

    def calculate_next_volume(self):
        """Calculate lowest volume not in collection"""
        index = 0
        for num in self.vol_arr:
            for i in range(0, 32):
                if num & (1 << i) == 0:
                    return index * 32 + i + 1
            index += 1
        print("Next volume for %s would exceed volume limit" % self.name)
        return index * 32 + 1

    def add_series_to_database(self, data_mgr):
        """
        add_series_to_database()
        Takes a series and adds it to the database if the database
        contains no entries with the same name as series.

        Returns True on success, False on failure.
        """
        cur = data_mgr.query("SELECT name FROM Series WHERE name='{0}'"
                             .format(self.name.replace("'", "''")))
        entries = cur.fetchall()

        if not entries:
            data_mgr.query("INSERT INTO Series VALUES("
                           "'{0}','{1}',{2},{3},'{4}','{5}','{6}')"
                           .format(
                               self.name.replace("'", "''"),
                               self.volumes_owned,
                               self.is_completed,
                               self.next_volume,
                               self.publisher.replace("'", "''"),
                               self.author.replace("'", "''"),
                               self.alt_names.replace("'", "''")))
            return True

        return False

    def edit(self, data_mgr):
        """
        edit()
        Allows user to modify all fields of a series. User selects field
        to modify from menu, continuing until user decides to save.
        Automatically updates dependent fields (ex. next volume)
        Returns True if the series has no volumes and the user chooses
        to delete it, False otherwise
        """
        reserved_words = ["unknown"]

        selection = ''
        while selection not in ('e', 'E'):
            selection = input("Edit: \n[N]ame / [V]olumes / [A]uthor / "
                              "[P]ublisher \n[Alt]ernate Names /"
                              "[C]ompletion Status / [E]nd: ")
            # Change Name
            if selection in ('n', 'N'):
                print("Current Name: {0}".format(self.name))
                series_name = input("Enter new series name or leave "
                                    "blank if unchanged: ")
                if series_name == "":
                    print("Name not changed.")
                elif series_name.lower() in reserved_words:
                    print("'{0}' is a reserved word. Name not changed."
                          .format(series_name))
                else:
                    cur = data_mgr.query("Select name FROM Series WHERE "
                                         "name = '{0}'"
                                         .format(series_name
                                                 .replace("'", "''")))
                    row = cur.fetchall()
                    if row:
                        print("New name already present in database,"
                              "not changed")
                    else:
                        self.name = series_name
                        print("Name changed to \"{0}\".".format(series_name))

            # Change Volumes
            elif selection in ('v', 'V'):
                print("Volumes Owned: {0}".format(self.get_volumes_owned()))
                if self.edit_volumes():
                    return True

            # Change Author
            elif selection in ('a', 'A'):
                print("Current Author: {0}".format(self.author))
                author = input("Enter author or leave blank if unchanged: ")
                if author == "":
                    pass
                else:
                    self.author = author
                    print("Author changed to \"{0}\".".format(author))

            # Change Publisher
            elif selection in ('p', 'P'):
                print("Current Publisher: {0}".format(self.publisher))
                publisher = input("Enter publisher or leave blank "
                                  "if unchanged: ")
                if publisher == "":
                    pass
                else:
                    self.publisher = publisher
                    print("Publisher changed to \"{0}\".".format(publisher))

            # Change Alternate Names
            elif selection.lower() == "alt":
                print("Current Alt. Names: {0}".format(self.alt_names))
                alt_names = input("Enter any alternate names for this series: ")
                if alt_names != "":
                    self.alt_names = alt_names

            # Change Completion Status
            elif selection in ('c', 'C'):
                is_completed = input("Have you completed this series? (y/n)"
                                     "(Leave blank if unchanged): ")
                if is_completed not in ('y', 'Y', 'n', 'N'):
                    pass
                elif is_completed in ('y', 'Y'):
                    is_completed = 1
                else:
                    is_completed = 0

            print("----------------------------------------")
            print(self.full_string())
            print("----------------------------------------")

        save_series = input("Save changes? (y/N): ")
        if save_series in ('y', 'Y'):
            self.update_database_entry(data_mgr)

        return False

    def edit_volumes(self):
        """
        edit_volumes()
        Changes which volumes are marked as owned in
        the series object.
        Returns True if the series has no volumes and the user
        chooses to delete it, False otherwise.
        """
        change_volumes = input("[A]dd or [R]emove volumes, or leave "
                               "blank if unchanged: ")

        # Add Volumes
        if change_volumes in ('a', 'A'):
            volumes_to_add = input(
                "Enter volumes to add (ex. 1, 3-5): ")

            volumes_to_add = generate_volumes_owned(volumes_to_add)
            vol_arr_to_add = [int(x) for x in
                              volumes_to_add.split(",")]
            self.vol_arr = [x | y for x, y in
                            zip(vol_arr_to_add, self.vol_arr)]

            # update related fields
            self.next_volume = self.calculate_next_volume()
            self.volumes_owned_readable = ""
            self.volumes_owned = generate_volumes_owned(
                self.get_volumes_owned())

        # Remove Volumes
        if change_volumes in ('r', 'R'):
            volumes_to_rmv = input(
                "Enter volumes to remove (ex. 1, 3-5): ")

            volumes_to_rmv = generate_volumes_owned(volumes_to_rmv)
            vol_arr_to_remove = [int(x) for x in
                                 volumes_to_rmv.split(",")]
            self.vol_arr = [~x & y for x, y in
                            zip(vol_arr_to_remove, self.vol_arr)]

            print(self.vol_arr)
            if all(not x for x in self.vol_arr):
                user_input = input("No volumes owned for series. "
                                   "Remove from database? (y/N): ")
                if user_input in ('y', 'Y'):
                    return True


            # update related fields
            self.next_volume = self.calculate_next_volume()
            self.volumes_owned_readable = ""
            self.volumes_owned = generate_volumes_owned(
                self.get_volumes_owned())

        return False

    def update_database_entry(self, data_mgr):
        """
        update_database_entry()
        Updates all fields in database for series based on unique identifier;
        adds series to database if not currently in database
        """
        if self.rowid is None:
            self.add_series_to_database(data_mgr)
            return

        data_mgr.query("UPDATE Series SET "
                       "name = '{0}', "
                       "volumes_owned = '{1}', "
                       "is_completed = {2}, "
                       "next_volume = {3}, "
                       "publisher = '{4}', "
                       "author = '{5}', "
                       "alt_names = '{6}' WHERE ROWID = {7}".format(
                           self.name.replace("'", "''"),
                           self.volumes_owned,
                           self.is_completed,
                           self.next_volume,
                           self.publisher.replace("'", "''"),
                           self.author.replace("'", "''"),
                           self.alt_names.replace("'", "''"),
                           self.rowid))
        print("Series updated!")
        return

    def compact_string(self):
        """
        compact_string()
        Returns a one-line string representation of the Series object
        """
        result = (self.name + " by " + self.author + " (" +
                  ("Completed)" if self.is_completed
                   else "Next Volume: %d)" % self.next_volume))
        return result

    def full_string(self):
        """
        full_string()
        Returns a multi-line string representation of the Series object
        """
        result = (self.name + ": " + self.get_volumes_owned() +
                  " (Completed: " + self.get_is_completed() + ")\n" +
                  "Alternate names: " + self.alt_names + "\n"
                  "Author: " + self.author + "\n"
                  "Published by: " + self.publisher +
                  ("\nNext Volume: %d" % self.next_volume
                   if not self.is_completed else ""))
        return result

    def __str__(self):
        """
        __str__()
        Returns a string representation of the object (defaults to
        full_string()
        """
        if Config().compact_list:
            return self.compact_string()
        return self.full_string()

def init_database(data_mgr, new_db_needed=True):
    """
    init_database()
    Initializes a DatabaseManager() object for use
    storing data for Series objects

    Passed as argument to DatabaseManager() constructor
    """
    data_mgr.query("SELECT name FROM sqlite_master "\
                   "WHERE type='table' AND name='Series'")

    if data_mgr.cur.fetchone() is None:
        data_mgr.query("CREATE TABLE Series(name TEXT, volumes_owned TEXT, "
                       "is_completed INT, next_volume INT, publisher TEXT, "
                       "author TEXT, alt_names TEXT, PRIMARY KEY(name))")
        if new_db_needed:
            next_series = input_series(data_mgr)
            while next_series is not None:
                if next_series.add_series_to_database(data_mgr):
                    print(next_series)
                else:
                    print("Failed to add series! (name conflict)")
                next_series = input_series(data_mgr)

def generate_volumes_owned(vol_list):
    """
    generate_volumes_owned(vol_list):

    Takes a string of numbers in a comma-separated list (ex. "1, 3-5, 7"),
    stores them bitwise in 32-bit integers, then concatenates bitwise
    representations of them in a string and returns the result
    """
    volume_limit = Config().volume_limit
    arr_length = int(math.ceil(volume_limit / 32))
    vol_arr = [0 for x in range(0, arr_length)]
    entered_values = [x.strip() for x in vol_list.split(',')]
    for num in entered_values:
        if num in ('', 'None'): # empty string, no volumes
            continue
        if '-' in num: # two integers separated by dash
            # should always have 2 integers
            nums = [int(k) for k in num.split('-')]
            if nums[0] < 1:
                print("Start volume must be greater than zero; "\
                      "token %s ignored" % num)
                continue
            if nums[1] > volume_limit:
                print("End volume too high; consider raising volume limit "\
                      "(currently {0})".format(volume_limit))
                nums[1] = 128
            for i in range(nums[0]-1, nums[1]):
                vol_arr[i // 32] |= 1 << (i % 32)
        else: # single integer
            try:
                num = int(num) - 1
            except ValueError:
                print("Invalid token: {0}".format(num))
                continue
            if num < 0:
                print("Token {0} ignored; volume number must be "\
                      "greater than zero".format(num))
                continue
            if num >= volume_limit:
                print("Token {0} ignored; volume number must be lower "\
                      "than volume limit (currently {1})"
                      .format(num, volume_limit))
                continue
            vol_arr[num // 32] |= 1 << (num % 32)
    result = ""
    for num in vol_arr:
        result += format(num) + ','
    return result[:-1]

def input_series(data_mgr):
    """
    input_series():

    Gets values for the name of a manga series, volumes currently owned,
    and whether the series is completed, and returns a Series() object
    """
    reserved_words = ["unknown"]

    series_name = input("Enter manga name or leave blank to cancel: ")
    if series_name == "":
        return None

    if series_name.lower() in reserved_words:
        print("'{0}' is a reserved word and cannot be used."
              .format(series_name))
        return None
    # try:
    cur = data_mgr.query("Select name FROM Series WHERE name = '{0}'"
                         .format(series_name.replace("'", "''")))
    row = cur.fetchall()
    if row:
        print("Name already in database!")
        return None
    # except:
    #     print("Database query failed, continuing...")
    volumes_raw = input("Enter volumes owned (if any) (ex. 1, 3-5): ")
    volumes_owned = generate_volumes_owned(volumes_raw)

    author = input("Enter author or leave blank if unknown: ")
    if author == "":
        author = "Unknown"

    publisher = input("Enter publisher (leave blank if unknown): ")
    if publisher == "":
        publisher = "Unknown"

    alt_names = input("Enter any alternate names for this series, if any: ")

    is_completed = input("Have you completed this series? (y/N): ")
    if is_completed not in ('y', 'Y'):
        is_completed = 0
    else:
        is_completed = 1

    return Series(name=series_name,
                  volumes_owned=volumes_owned,
                  is_completed=is_completed,
                  next_volume=-1,
                  publisher=publisher,
                  author=author, alt_names=alt_names)

class EditSeries():
    def name(self, series, name):
        reserved_words = ["unknown"]
        
        if not name:
            print("Name not changed.")
            return (1, "No name entered")
        elif name.lower() in reserved_words:
            print("'{0}' is a reserved word. Name not changed."
                  .format(name))
            return (2, "{0} is a reserved word".format(name))
        else:
            cur = data_mgr.query("Select name FROM Series WHERE "
                                 "name = '{0}'"
                                 .format(name
                                         .replace("'", "''")))
            row = cur.fetchall()
            if row:
                print("New name already present in database,"
                      "not changed")
                return (3, "Name already present in database")
            else:
                series.name = name
                print("Name changed to \"{0}\".".format(series_name))
                return (0, "")

    def volumes(self, series, vol_str):
        ### STUB
        return 1

    def author(self, series, author):
        if author:
            series.author = author
            return (0, "")
        return (1, "No author name entered")

    def publisher(self, series, publisher):
        if publisher:
            series.publisher = publisher
            return (0, "")
        return (1, "No publisher name entered")

    def alt_names(self, series, alt_names):
        if alt_names:
            series.alt_names = alt_names
            return (0, "")
        return (1, "No alternate names entered")

    def completion(self, series, completion):
        positive_inputs = ["y", "complete", "yes", "1"]
        negative_inputs = ["n", "incomplete", "no", "0"]
        if completion.lower() in positive_inputs:
            series.is_completed = 1
            return (0, "")
        elif completion.lower() in negative_inputs:
            series.is_completed = 0
            return (0, "")
        return (1, "Invalid value for completion status")
