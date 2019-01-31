#!/usr/bin/env python3
# MangaTracker
# Program to track owned and desired manga series

import os
import math
import configparser
from DatabaseManager import DatabaseManager

# Global constants - fallback in case config.ini cannot be read

DATABASE_NAME = "manga.db"
VOLUME_LIMIT = 128
PAGINATED = False
SERIES_PER_PAGE = 5
COMPACT_LIST = True

class Series(object):
    """
    Series(object)
    A single manga series. Contains the name of the series, the number of
    volumes currently owned, whether the series is completed
    """
    # TODO: modify to use kwargs instead of arguments
    # def __init__(self, name, volumes_owned, is_completed,
    #              next_volume=-1, publisher='Unknown', author='Unknown',
    #              alt_names='', rowid=None):
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
        """
        valid_keys = ["name", "volumes_owned", "is_completed",
                      "next_volume", "publisher", "author",
                      "alt_names", "rowid"]
        next_vol_found = False

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
        if self.next_volume == -1:
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
                last = VOLUME_LIMIT
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

    # def get_next_volume(self):
    #     """Returns the lowest-numbered volume not in collection"""
    #     # check if calculated, otherwise return current value
    #     if self.next_volume <= 0:
    #         self.next_volume = self.calculate_next_volume()
    #     return self.next_volume

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

        if len(entries) == 0:
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

    # TODO: Show current value when editing
    def edit(self, data_mgr):
        """
        edit()
        Allows user to modify all fields of a series. User selects field
        to modify from menu, continuing until user decides to save.
        Automatically updates dependent fields (ex. next volume)
        """
        selection = ''
        while selection != 'e' and selection != 'E':
            selection = input("Edit: \n[N]ame / [V]olumes / [A]uthor / "
                              "[P]ublisher \n[Alt]ernate Names /"
                              "[C]ompletion Status / [E]nd: ")
            if selection == 'n' or selection == 'N':
                series_name = input("Enter series name or leave "
                                    "blank if unchanged: ")
                if series_name == "":
                    print("Name not changed.")
                    pass
                else:
                    cur = data_mgr.query("Select name FROM Series WHERE "
                                         "name = '{0}'"
                                         .format(series_name
                                                 .replace("'", "''")))
                    row = cur.fetchall()
                    if len(row) > 0:
                        print("Name already present in database, not changed")
                    else:
                        self.name = series_name
                        print("Name changed to \"{0}\".".format(series_name))
            elif selection == 'v' or selection == 'V':
                change_volumes = input("[A]dd or [R]emove volumes, or leave "
                                       "blank if unchanged: ")

                # Add Volumes
                if change_volumes == "a" or change_volumes == "A":
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
                if change_volumes == "r" or change_volumes == "R":
                    volumes_to_rmv = input(
                        "Enter volumes to remove (ex. 1, 3-5): ")

                    volumes_to_rmv = generate_volumes_owned(volumes_to_rmv)
                    vol_arr_to_remove = [int(x) for x in
                                         volumes_to_rmv.split(",")]
                    self.vol_arr = [~x & y for x, y in
                                    zip(vol_arr_to_remove, self.vol_arr)]

                    # update related fields
                    self.next_volume = self.calculate_next_volume()
                    self.volumes_owned_readable = ""
                    self.volumes_owned = generate_volumes_owned(
                        self.get_volumes_owned())

            # Change Author
            elif selection == 'a' or selection == 'A':
                author = input("Enter author or leave blank if unchanged: ")
                if author == "":
                    pass
                else:
                    self.author = author
                    print("Author changed to \"{0}\".".format(author))

            # Change Publisher
            elif selection == 'p' or selection == 'P':
                publisher = input("Enter publisher or leave blank "
                                  "if unchanged: ")
                if publisher == "":
                    pass
                else:
                    self.publisher = publisher
                    print("Publisher changed to \"{0}\".".format(publisher))

            # Change Alternate Names
            elif selection.lower() == "alt":
                alt_names = input("Enter any alternate names for this series: ")
                if alt_names != "":
                    self.alt_names = alt_names

            # Change Completion Status
            elif selection == 'c' or selection == 'C':
                is_completed = input("Is this series completed? (y/N) (Leave "
                                     "blank if unchanged): ")
                if is_completed == "":
                    pass
                elif is_completed != 'y' and is_completed != 'Y':
                    is_completed = 0
                else:
                    is_completed = 1

            print("----------------------------------------")
            print(self)
            print("----------------------------------------")

        save_series = input("Save changes? (y/N): ")
        if save_series == 'y' or save_series == 'Y':
            self.update_database_entry(data_mgr)

    def edit_series_old(self, data_mgr):
        """
        edit_series()
        Allow user to change all fields in series. Follows similar
        structure to input_series()
        """
        series_name = input("Enter series name or leave blank if unchanged: ")
        if series_name == "":
            print("Name not changed.")
            pass
        else:
            cur = data_mgr.query("Select name FROM Series WHERE name = '{0}'"
                                 .format(series_name.replace("'", "''")))
            row = cur.fetchall()
            if len(row) > 0:
                print("Name already present in database, not changed")
            else:
                self.name = series_name
                print("Name changed to \"{0}\".".format(series_name))

        #change_volumes = input("[A]dd volumes / [R]emove volumes / "
        #                       "[C]ontinue: ")
        # add volumes, remove volumes, continue without modifying
        # volumes_raw = input("Enter volumes owned (if any) (ex. 1, 3-5): ")
        # volumes_owned = generate_volumes_owned(volumes_raw)
        change_volumes = input("[A]dd or [R]emove volumes, or leave "
                               "blank if unchanged: ")

        if change_volumes == "a" or change_volumes == "A":
            volumes_to_add = input("Enter volumes to add (ex. 1, 3-5): ")
            volumes_to_add = generate_volumes_owned(volumes_to_add)
            vol_arr_to_add = [int(x) for x in volumes_to_add.split(",")]
            print(self.vol_arr)
            self.vol_arr = [x | y for x, y in
                            zip(vol_arr_to_add, self.vol_arr)]
            print(self.vol_arr)
            # NEXT STEPS:
            # update next volume, volumes_owned_readable, volumes_owned
            self.next_volume = self.calculate_next_volume()
            self.volumes_owned_readable = ""
            self.volumes_owned = generate_volumes_owned(
                self.get_volumes_owned())

        if change_volumes == "r" or change_volumes == "R":
            volumes_to_remove = input("Enter volumes to remove (ex. 1, 3-5): ")
            volumes_to_remove = generate_volumes_owned(volumes_to_remove)
            vol_arr_to_remove = [int(x) for x in volumes_to_remove.split(",")]
            print(self.vol_arr)
            self.vol_arr = [~x & y for x, y in
                            zip(vol_arr_to_remove, self.vol_arr)]
            print(self.vol_arr)
            # update related fields
            self.next_volume = self.calculate_next_volume()
            self.volumes_owned_readable = ""
            self.volumes_owned = generate_volumes_owned(
                self.get_volumes_owned())

        author = input("Enter author or leave blank if unchanged: ")
        if author == "":
            pass
        else:
            self.author = author
            print("Author changed to \"{0}\".".format(author))

        publisher = input("Enter publisher or leave blank if unchanged: ")
        if publisher == "":
            pass
        else:
            self.publisher = publisher
            print("Publisher changed to \"{0}\".".format(publisher))

        # only change if no entry exists
        alt_names = input("Enter any alternate names for this series: ")
        if self.alt_names == "" and alt_names != "":
            self.alt_names = alt_names

        is_completed = input("Is this series completed? (y/N) (Leave "
                             "blank if unchanged): ")
        if is_completed == "":
            pass
        elif is_completed != 'y' and is_completed != 'Y':
            is_completed = 0
        else:
            is_completed = 1

    def update_database_entry(self, data_mgr):
        """
        update_database_entry()
        Updates all fields in database for series based on unique identifier;
        adds series to database if not currently in database
        """
        if self.rowid == None:
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
        return self.full_string()

def entry_to_series(entry):
    """
    entry_to_series()
    Takes a single row from a database query and converts it
    into a series.
    """
    series = Series(name=str(entry[1]),          # Series Name
                    volumes_owned=str(entry[2]), # Volumes Owned
                    is_completed=entry[3],       # Is Completed
                    next_volume=entry[4],        # Next Volume
                    publisher=str(entry[5]),     # Publisher
                    author=str(entry[6]),        # Author
                    alt_names=str(entry[7]),     # Alternate Names
                    rowid=entry[0])              # Row ID (for updates)
    return series

def print_database(data_mgr):
    """
    print_database(data_mgr)
    Print status of all series in database
    """
    cur = data_mgr.query("SELECT rowid, * FROM Series ORDER BY name")
    entries = cur.fetchall()
    count = 0
    for entry in entries:
        if PAGINATED and count != 0 and count % SERIES_PER_PAGE == 0:
            print("----------------------------------------")
            continue_print = input("Press Enter to continue "
                                   "or type 'q' to stop: ")
            if continue_print == 'q' or continue_print == 'Q':
                return

        print("----------------------------------------")
        series = entry_to_series(entry)
        print(series)
        count += 1

    if len(entries) > 0:
        print("----------------------------------------")

def input_series(data_mgr):
    """
    input_series():
    Gets values for the name of a manga series, volumes currently owned,
    and whether the series is completed, and returns a Series() object
    """
    series_name = input("Enter manga name or leave blank to cancel: ")
    if series_name == "":
        return None
    # try:
    cur = data_mgr.query("Select name FROM Series WHERE name = '{0}'"
                         .format(series_name.replace("'", "''")))
    row = cur.fetchall()
    if len(row) > 0:
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

    is_completed = input("Is this series completed? (y/N): ")
    if is_completed != 'y' and is_completed != 'Y':
        is_completed = 0
    else:
        is_completed = 1

    return Series(name=series_name,
                  volumes_owned=volumes_owned,
                  is_completed=is_completed,
                  next_volume=-1,
                  publisher=publisher,
                  author=author, alt_names=alt_names)

def generate_volumes_owned(str):
    """
    generate_volumes_owned(str):
    Takes a string of numbers in a comma-separated list (ex. "1, 3-5, 7"),
    stores them bitwise in 32-bit integers, then concatenates bitwise
    representations of them in a string and returns the result
    """
    arr_length = int(math.ceil(VOLUME_LIMIT / 32))
    vol_arr = [0 for x in range(0, arr_length)]
    entered_values = [x.strip() for x in str.split(',')]
    for num in entered_values:
        if num == '' or num == "None": # empty string, no volumes
            continue
        if '-' in num: # two integers separated by dash
            # should always have 2 integers
            nums = [int(k) for k in num.split('-')]
            if nums[0] < 1:
                print("Start volume must be greater than zero; "\
                      "token %s ignored" % num)
                continue
            if nums[1] > VOLUME_LIMIT:
                print("End volume too high; consider raising volume limit "\
                      "(currently {0})".format(VOLUME_LIMIT))
                nums[1] = 128
            for i in range(nums[0]-1, nums[1]):
                vol_arr[i // 32] |= 1 << (i % 32)
        else: # single integer
            try:
                num = int(num) - 1
            except:
                print("Invalid token: {0}".format(num))
                continue
            if num < 0:
                print("Token {0} ignored; volume number must be "\
                      "greater than zero".format(num))
                continue
            if num >= VOLUME_LIMIT:
                print("Token {0} ignored; volume number must be lower "\
                      "than volume limit (currently {1})"
                      .format(num, VOLUME_LIMIT))
                continue
            vol_arr[num // 32] |= 1 << (num % 32)
    result = ""
    for num in vol_arr:
        result += format(num) + ','
    return result[:-1]

def set_default_config(filename):
    """
    set_default_config()
    Saves default config to desired filename
    """
    if os.path.isfile(filename):
        os.remove(filename)

    config = configparser.ConfigParser()
    default_cfg = {'config': {'database_name' : 'manga.db',
                              'volume_limit' : 128,
                              'paginated' : 0,
                               'series_per_page' : 5}}

    config.read_dict(default_cfg)
    with open('config.ini', 'w') as config_ini:
        config.write(config_ini)

def print_entries_list(entries):
    """
    print_entries_list()
    Function to print all items matching database query
    """
    count = 0

    for entry in entries:
        if PAGINATED and count != 0 and count % SERIES_PER_PAGE == 0:
            print("----------------------------------------")
            continue_print = input("Press Enter to continue "
                                   "or type 'q' to stop: ")
            if continue_print == 'q' or continue_print == 'Q':
                return

        print("----------------------------------------")
        series = entry_to_series(entry)
        print(series)
        count += 1

    if len(entries) > 0:
        print("----------------------------------------")

def list_series(DATA_MGR):
    selection = input("List [A]ll / [C]omplete / "
                      "[I]ncomplete / Series with [G]aps: ")
    # Completed Series
    if selection == 'c' or selection == 'C':
        cur = DATA_MGR.query("SELECT rowid, * FROM Series WHERE "
                             "is_completed = 1 ORDER BY name")
        entries = cur.fetchall()

        if len(entries) == 0:
            print("No completed series found.")
            return

        print("Found {0} completed series:".format(len(entries)))
        print_entries_list(entries)
        return

    # Incomplete Series
    if selection == 'i' or selection == 'I':
        cur = DATA_MGR.query("SELECT rowid, * FROM Series WHERE "
                             "is_completed = 0 ORDER BY name")
        entries = cur.fetchall()

        if len(entries) == 0:
            print("No incomplete series found.")
            return

        print("Found {0} incomplete series:".format(len(entries)))
        print_entries_list(entries)
        return

    # Series with Gaps
    if selection == 'g' or selection == 'G':
        cur = DATA_MGR.query("SELECT rowid, * FROM Series ORDER BY name")
        entries = cur.fetchall()
        series_list = [entry_to_series(entry) for entry in entries]
        series_with_gaps = []

        for series in series_list:
            binary_str = series.get_volumes_owned_binary()
            if regexp("1*0+1", binary_str):
                series_with_gaps.append(series)

        if len(series_with_gaps) == 0:
            print("No series with gaps found.")
            return

        print("Found {0} series with gaps:".format(
            len(series_with_gaps)))

        count = 0
        for series in series_with_gaps:
            if PAGINATED and count != 0 and count % SERIES_PER_PAGE == 0:
                print("----------------------------------------")
                continue_print = input("Press Enter to continue "
                                       "or type 'q' to stop: ")
                if continue_print == 'q' or continue_print == 'Q':
                    return

            print("----------------------------------------")
            print(series)
            #print("----------------------------------------")
            count += 1

        if len(series_with_gaps) > 0:
            print("----------------------------------------")
            return

    # Default (print all)
    print_database(DATA_MGR)

def search_for_series(data_mgr):
    """
    search_for_series()
    Takes a DatabaseManager object, queries the database for a
    search term given by user, returns the search term and
    any matching entries
    """
    search_term = input("Search for series by name or publisher: ")
    cur = data_mgr.query("SELECT rowid, * FROM Series WHERE "
                         "name LIKE '%{0}%' OR "
                         "publisher LIKE '%{0}%' OR "
                         "author LIKE '%{0}%' OR "
                         "alt_names LIKE '%{0}%'"
                         "ORDER BY name"
                         .format(search_term))
    entries = cur.fetchall()
    return (entries, search_term)

def main():
    """
    main()
    Main driver function for mangatracker program
    """
    if not os.path.isfile("config.ini"):
        set_default_config("config.ini")

    config = configparser.ConfigParser()
    config.read('config.ini')

    global DATABASE_NAME
    global VOLUME_LIMIT
    global PAGINATED    
    global SERIES_PER_PAGE

    DATABASE_NAME = config.get('config', 'database_name')
    VOLUME_LIMIT = config.getint('config', 'volume_limit')
    PAGINATED = config.getboolean('config', 'paginated')
    SERIES_PER_PAGE = config.getint('config', 'series_per_page')

    DATA_MGR = DatabaseManager(DATABASE_NAME)
    print_database(DATA_MGR)

    while True:
        user_input = input("[S]earch, [L]ist, [A]dd, "
                           "[E]dit, [O]ptions, E[x]it: ")

        if user_input == 'x' or user_input == 'X':
            break

        if user_input == 's' or user_input == 'S':
            # TODO: color matching text (maybe not?)
            entries, search_term = search_for_series(DATA_MGR)

            print()
            if len(entries) == 0:
                print("No series found for '{0}'."
                      .format(search_term))
                continue

            print("Found {0} entries for '{1}':"
                  .format(len(entries), search_term))
            print_entries_list(entries)
            continue

        if user_input == 'l' or user_input == 'L':
            list_series(DATA_MGR)

        # Add Series
        if user_input == 'a' or user_input == 'A':
            try:
                new_series = input_series(DATA_MGR)
            except KeyboardInterrupt:
                print("\nAdd series operation cancelled")
                new_series = None

            if new_series != None:
                new_series.add_series_to_database(DATA_MGR)
                print("----------------------------------------")
                print(new_series)
                print("----------------------------------------")

            continue

        # Edit Series
        if user_input == 'e' or user_input == 'E':
            entries, search_term = search_for_series(DATA_MGR)
            count = 0

            print()
            if len(entries) == 0:
                print("No series found for '{0}'."
                      .format(search_term))
                continue

            print("Found {0} entries for '{1}':"
                  .format(len(entries), search_term))

            for entry in entries:
                print("----------------------------------------")
                series = entry_to_series(entry)
                print(series)
                print("----------------------------------------")
                
                found_series = input("Edit this series? (y/N/q): ")
                if found_series == 'q' or found_series == 'Q':
                    break
                if found_series == 'y' or found_series == 'Y':
                    series.edit(DATA_MGR)
                    break

                count += 1
                if count != len(entries):
                    print("Next Series:")

        # Options
        if user_input == 'o' or user_input == 'O':
            print("-- OPTIONS --")
            print("1. Change Database Name")
            print("2. Change Volume Limit")
            print("3. Change Series Displayed Per Page")
            print("4. Reset to Default Settings")
            print("5. Clear Database")
            option = input("Enter a number to modify option: ")
            try:
                option = int(option)
                config = configparser.ConfigParser()
                config.read("config.ini")

                # 1. Change database name
                if option == 1:
                    new_db_name = input("Enter new database name, or leave "\
                                        "blank to leave unchanged: ")
                    if new_db_name != "" and not os.exists(new_db_name):
                        os.rename(DATABASE_NAME, new_db_name)
                        config["config"]["database_name"] = new_db_name
                        DATABASE_NAME = new_db_name
                        with open("config.ini", "w") as config_ini:
                            config.write(config_ini)
                    else:
                        print("Database name not changed.")

                # 2. Change volume limit
                elif option == 2:
                    # TODO: allow changing volume limit
                    #      (needs some way to change existing database entries
                    print("Currently, volume limit is hard-coded; changing it"
                          "may cause issues. Functionality will be added at"
                          "a later date.")
                    pass

                # 3. Change series per page ( 0 for no limit)
                elif option == 3:
                    new_series_per_page = input("Enter maximum number of "
                                                "series to display per page, "
                                                "or 0 to not use pages: ")
                    if new_series_per_page == '0':
                        config["config"]["paginated"] = 0
                        PAGINATED = False
                        with open("config.ini", "w") as config_ini:
                            config.write(config_ini)
                    try:
                        new_series_per_page = int(new_series_per_page)
                        if new_series_per_page < 1:
                            print("Series per page must be greater than 1!")
                        else:
                            config["config"]["series_per_page"] = (
                                new_series_per_page)
                            config["config"]["paginated"] = 1
                            SERIES_PER_PAGE = new_series_per_page
                            PAGINATED = True
                            with open("config.ini", "w") as config_ini:
                                config.write(config_ini)
                    except Exception:
                        pass

                # 4. Reset to default
                elif option == 4:
                    default = input("Reset all settings to default? (y/N): ")
                    if default == 'y' or default == 'Y':
                        set_default_cfg("config.ini")

                # 5. Clear database (Does not prompt user for series)
                elif option == 5:
                    delete_database = input("Remove Database? "\
                                            "(will copy to {0}.bak) y/N: "
                                            .format(DATABASE_NAME))
                    if delete_database == 'y' or delete_database == 'Y':
                        os.rename(DATABASE_NAME, DATABASE_NAME+".bak")
                        DATA_MGR = DatabaseManager(False)

            except Exception:
                print("Returning to main screen")

# TESTING CODE
def series_test():
    """
    Test function to check Series class functionality
    """
    test_failed = False
    # TEST 1: generate_volumes_owned produces correct output #
    print("**TEST 1: generate_volumes_owned()**")
    try:
        vol_owned1 = generate_volumes_owned("1, 3-5, 7, 52 ")
        correct_vol_owned1 = "93,524288,0,0"
        if vol_owned1 != correct_vol_owned1:
            print("Failure! Actual: {0} != Expected {1}".format(
                vol_owned1, correct_vol_owned1))
            test_failed = True
    except:
        print("Error generating volumes for '1, 3-5, 7, 52 '")
    # should produce error messages
    try:
        generate_volumes_owned("-1, 1, 3")
    except:
        print("Error generating volumes for '-1, 1, 3'")

    try:
        generate_volumes_owned("1, 3, %d" % (VOLUME_LIMIT + 1))
    except:
        print("Error generating volumes for '1, 3, %d'" % (VOLUME_LIMIT + 1))

    if test_failed:
        print("**TEST 1 FAILED**")
    else:
        print("**TEST 1 PASSED**")

    test_failed = False
    print()

    # TEST 2: Creating Series() objects
    print("**TEST 2: Series()**")
    try:
        vol_owned = generate_volumes_owned("1, 3-5, 7, 52 ")
        series1 = Series("test 1", vol_owned, 'n')
        print("Series1:")
        if series1.name != "test 1":
            print("Name does not match expected value!")
            test_failed = True
        if series1.get_volumes_owned() != "1, 3-5, 7, 52":
            print(series1.get_volumes_owned())
            print("Volumes owned does not match expected value!")
            test_failed = True
        if series1.get_next_volume() != 2:
            print("Next volume does not match expected value!")
            test_failed = True
        print(series1.get_is_completed())
        print(series1)
    except:
        print("Error creating series or checking variables within series")

    if test_failed:
        print("**TEST 2 FAILED**")
    else:
        print("**TEST 2 PASSED**")

    test_failed = False
    print()
    # series2 = input_series()
    # print("Series2:")
    # print(series2.get_name())
    # print(series2.get_volumes_owned())
    # print(series2.get_next_volume())
    # print(series2.get_is_completed())

    # TEST 3: DatabaseManager and related functions
    data_mgr = DatabaseManager("test.db")
    data_mgr.add_series_to_database(series1)
    print_database(data_mgr)
    os.remove("test.db")

if __name__ == "__main__":
    main()
