# MangaTracker
# Program to track owned and desired manga series

import sqlite3 as lite
import os
import math
import configparser

# Global constants - fallback in case config.ini cannot be read

DATABASE_NAME = "manga.db"
VOLUME_LIMIT = 128
PAGINATED = False
SERIES_PER_PAGE = 5
    
class DatabaseManager(object):
    """
    DatabaseManager(object)
    Main interface between program and SQLite3 database
    """
    def __init__(self, new_db_needed=False):
        self.con = lite.connect(DATABASE_NAME)
        self.cur = self.con.cursor()
        self.query("SELECT name FROM sqlite_master "\
                   "WHERE type='table' AND name='Series'")
        if self.cur.fetchone() == None: 
            self.query("CREATE TABLE Series(name TEXT, volumes_owned TEXT, "\
                       "is_completed INT, next_volume INT, publisher TEXT)")
            next_series = input_series(self)
            while next_series != None:
                self.add_series_to_database(next_series)
                print(next_series)
                next_series = input_series(self)
    
    def add_series_to_database(self, series):
        self.query("INSERT INTO Series VALUES('{0}','{1}',{2},{3},'{4}')"
                   .format(
                       series.name.replace("'", "''"),
                       series.volumes_owned,
                       series.is_completed,
                       series.get_next_volume(),
                       series.publisher.replace("'", "''")))

    def query(self, arg):
        self.cur.execute(arg)
        self.con.commit()
        return self.cur

    def __del__(self):
        self.con.close()
        
class Series(object):
    """
    Series(object)
    A single manga series. Contains the name of the series, the number of
    volumes currently owned, whether the series is completed
    """
    def __init__(self, name, volumes_owned, is_completed, 
                 next_volume=-1, publisher='Unknown', rowid=None):
        self.name = name
        self.volumes_owned = volumes_owned
        self.is_completed = is_completed
        self.next_volume = next_volume
        self.publisher = publisher
        
        self.rowid = rowid
        self.vol_arr = [int(x) for x in volumes_owned.split(',')]
        self.volumes_owned_readable = ""

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
                    if first == -1 and num & (1 << i) != 0: # assuming sequential 
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
        return "Yes" if self.is_completed == 1 else "No"

    def get_next_volume(self):
        # check if calculated, otherwise return current value
        if self.next_volume <= 0:
            self.next_volume = self.calculate_next_volume()
        return self.next_volume


    def calculate_next_volume(self):
        index = 0
        for num in self.vol_arr:
            for i in range(0, 32):
                if num & (1 << i) == 0:
                    return index * 32 + i + 1
            index += 1
        print("Next volume for %s would exceed volume limit" % self.name)
        return index * 32 + 1
        
    def edit_series(self, data_mgr):
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
        
        change_volumes = input("[A]dd volumes / [R]emove volumes / "
                               "[C]ontinue: ")
        # add volumes, remove volumes, continue without modifying
        # volumes_raw = input("Enter volumes owned (if any) (ex. 1, 3-5): ")
        # volumes_owned = generate_volumes_owned(volumes_raw)

        publisher = input("Enter publisher or leave blank if unchanged: ")
        if publisher == "":
            print("Publisher not changed.")
            pass
        else:
            self.publisher = publisher
            print("Publisher changed to \"{0}\".".format(publisher))

        is_completed = input("Is this series completed? (y/N): ")
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
        if rowid == None:
            data_mgr.add_series_to_database(self)
            return
        data_mgr.query("UPDATE Series SET "\
                       "series_name = '{0}' AND "\
                       "volumes_owned = '{1}' AND "\
                       "is_completed = {2} AND "\
                       "next_volume = {3} AND "\
                       "publisher = '{4} WHERE ROWID = {5}".format(
                           self.name.replace("'", "''"),
                           self.volumes_owned,
                           self.is_completed,
                           self.get_next_volume(),
                           self.publisher.replace("'", "''"),
                           self.rowid))
        print("Series updated!")
        return
    
    def __str__(self):
        result = (self.name + ": " + self.get_volumes_owned() +
                  " (Completed: " + self.get_is_completed() + ")\n" +
                  "Published by: " + self.publisher + "\n" +
                  "Next Volume: %d" % self.get_next_volume())
        return result

def print_database(data_mgr):
    """
    print_database(data_mgr)
    Print status of all series in database
    """
    cur = data_mgr.query("SELECT rowid, * FROM Series")
    entries = cur.fetchall()
    count = 0
    for entry in entries:
        if PAGINATED and count != 0 and count % SERIES_PER_PAGE == 0:
            print("----------------------------------------")
            continue_print = input("Press Enter to continue or type 'q' to stop: ")
            if continue_print == 'q' or continue_print == 'Q':
                return

        print("----------------------------------------")
        series = Series(entry[1], # Series Name 
                        entry[2], # Volumes Owned
                        entry[3], # Is Completed
                        entry[4], # Next Volume
                        entry[5], # Publisher
                        entry[0]) # Row ID (for updates)
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

    publisher = input("Enter publisher (leave blank if unknown): ")
    if publisher == "":
        publisher = "Unknown"

    is_completed = input("Is this series completed? (y/N): ")
    if is_completed != 'y' and is_completed != 'Y':
        is_completed = 0
    else:
        is_completed = 1

    return Series(series_name, volumes_owned, is_completed, publisher=publisher)

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
        if num == '': # empty string, no volumes
            continue
        if '-' in num:
            nums = [int(k) for k in num.split('-')] # should always have 2 integers
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
        else:
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
    if os.path.isfile("config.ini"):
        os.remove("config.ini")

    config = configparser.ConfigParser()
    default_cfg = {'config': { 'database_name' : 'manga.db',
                               'volume_limit' : 128,
                               'paginated' : 0,
                               'series_per_page' : 5 } }

    config.read_dict(default_cfg)
    with open('config.ini', 'w') as config_ini:
        config.write(config_ini)

def main():
    """
    main()
    Main driver function for mangatracker program
    """
    if not os.path.isfile("config.ini"):
        set_default_cfg("config.ini")
    
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    DATABASE_NAME = config.get('config', 'database_name')
    VOLUME_LIMIT = config.getint('config', 'volume_limit')
    PAGINATED = config.getboolean('config', 'paginated')
    SERIES_PER_PAGE = config.getint('config', 'series_per_page')
        
    DATA_MGR = DatabaseManager()
    print_database(DATA_MGR)
    while True:
        user_input = input("[S]earch, [L]ist, [A]dd, [E]dit, [O]ptions, E[x]it: ")

        if user_input == 'x' or user_input == 'X':
            break

        if user_input == 's' or user_input == 'S':
            # TODO: allow user to search for a specific series, modify/delete
            #   entries, etc.
            # TODO: color matching text (maybe not?)
            search_term = input("Search for series by name or publisher: ")
            cur = DATA_MGR.query("SELECT rowid, * FROM Series WHERE "\
                                 "name LIKE '%{0}%' OR "\
                                 "publisher LIKE '%{0}%'"
                                 .format(search_term))
            entries = cur.fetchall()
            entries_converted = []
            count = 0
            
            print()
            if len(entries) == 0:
                print("No series found for '{0}'."
                      .format(search_term))
                continue
            print("Found {0} entries for '{0}':".format(len(entries)))
            for entry in entries:
                if PAGINATED and count != 0 and count % SERIES_PER_PAGE == 0:
                    print("----------------------------------------")
                    continue_print = input("Press Enter to continue or type 'q' to stop: ")
                    if continue_print == 'q' or continue_print == 'Q':
                        return

                print("----------------------------------------")
                series = Series(entry[1], # Series Name 
                                entry[2], # Volumes Owned
                                entry[3], # Is Completed
                                entry[4], # Next Volume
                                entry[5], # Publisher
                                entry[0]) # Row ID (for updates)
                print(series)
                count += 1

            if len(entries) > 0:
                print("----------------------------------------")
            continue

        if user_input == 'l' or user_input == 'L':
            # TODO: Add option to print all complete, incomplete volumes,
            #   series with gaps, etc.
            print_database(DATA_MGR)
            selection = input("List [A]ll / [C]omplete / "
                              "[I]ncomplete / Series with [G]aps: ")
            if selection == 'c' or selection == 'C':
                cur = DATA_MGR.query("SELECT rowid, * FROM Series WHERE "
                                     "is_completed = 1")
                entries = cur.fetchall()
                count = 0
                if len(entries) == 0:
                    print("No completed series found.")
                    continue
                print("Found {0} completed series:".format(len(entries)))
                for entry in entries:
                    print("----------------------------------------")
                    series = Series(entry[1], # Series Name 
                                entry[2], # Volumes Owned
                                entry[3], # Is Completed
                                entry[4], # Next Volume
                                entry[5], # Publisher
                                entry[0]) # Row ID (for updates)
                    print(series)
                    print("----------------------------------------")
                
            continue

        if user_input == 'a' or user_input == 'A':
            new_series = input_series(DATA_MGR)
            if(new_series != None):
                DATA_MGR.add_series_to_database(new_series)
            print("----------------------------------------")
            print(new_series)
            print("----------------------------------------")
            continue

        if user_input == 'e' or user_input == 'E':
            search_term = input("Search for series to edit by name or publisher: ")
            cur = DATA_MGR.query("SELECT rowid, * FROM Series WHERE "
                                 "name LIKE '%{0}%' OR "
                                 "publisher LIKE '%{0}%'"
                                 .format(search_term))
            entries = cur.fetchall()
            count = 0
            
            print()
            if len(entries) == 0:
                print("No series found for '{0}'."
                      .format(search_term))
                continue
            print("Found {0} entries for '{0}':".format(len(entries)))
            for entry in entries:
                print("----------------------------------------")
                series = Series(entry[1], # Series Name 
                                entry[2], # Volumes Owned
                                entry[3], # Is Completed
                                entry[4], # Next Volume
                                entry[5], # Publisher
                                entry[0]) # Row ID (for updates)
                print(series)
                print("----------------------------------------")
                found_series = input("Edit this series? (y/N/q): ")

                if found_series == 'q' or found_series == 'Q':
                    break
                if found_series == 'y' or found_series == 'Y':
                    series.edit_series(DATA_MGR)
                    
                    print("----------------------------------------")
                    print(series)
                    print("----------------------------------------")
                    
                    save_series = input("Save changes? (y/N): ")
                    if save_series == 'y' or save_series == 'Y':
                        series.update_database_entry(DATA_MGR)
                    break
                count += 1
                if count != len(entries):
                    print("Next Series:") # TODO: check for more series

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
                    print("Currently, volume limit is hard-coded; changing it"\
                          "may cause issues.")
                    pass

                # 3. Change series per page ( 0 for no limit)                
                elif option == 3:
                    new_series_per_page = input("Enter maximum number of series "\
                                                "to display per page, "\
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
                
                # 5. Clear database
                elif option == 5:
                    delete_database = input("Remove Database? "\
                                            "(will copy to {0}.bak) y/N: "
                                            .format(DATABASE_NAME))
                    if delete_database == 'y' or delete_database == 'Y':
                        os.rename(DATABASE_NAME, DATABASE_NAME+".bak")
                        
            except Exception:
                print("Returning to main screen")
                return

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
    
    if(test_failed):
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
    os.delete("test.db")

if __name__ == "__main__":
    main()
