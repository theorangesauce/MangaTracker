#!/usr/bin/env python3
# MangaTracker
# Program to track owned and desired manga series

import os
import math
import configparser
from DatabaseManager import DatabaseManager
from DatabaseManager import regexp
from Series import Series, init_database

# Global constants - fallback in case config.ini cannot be read

DATABASE_NAME = "manga.db"
VOLUME_LIMIT = 128
PAGINATED = False
SERIES_PER_PAGE = 5
COMPACT_LIST = True

def entry_to_series(entry):
    """
    entry_to_series()
    Takes a single row from a database query and converts it
    into a series.
    """
    global VOLUME_LIMIT
    global COMPACT_LIST

    series = Series(name=str(entry[1]),          # Series Name
                    volumes_owned=str(entry[2]), # Volumes Owned
                    is_completed=entry[3],       # Is Completed
                    next_volume=entry[4],        # Next Volume
                    publisher=str(entry[5]),     # Publisher
                    author=str(entry[6]),        # Author
                    alt_names=str(entry[7]),     # Alternate Names
                    rowid=entry[0],              # Row ID (for updates)
                    volume_limit=VOLUME_LIMIT,
                    compact_list=COMPACT_LIST)   # Config properties
    return series

def print_all_series(data_mgr):
    """
    print_all_series(data_mgr)
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
                              'series_per_page' : 5,
                              'compact_list': 0}}

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
    print_all_series(DATA_MGR)

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

def remove_series_from_database(data_mgr, series):
    """
    remove_series_from_database()
    Takes a DatabaseManager object and a Series object, and removes
    the associated series from the database
    """
    cur = data_mgr.query("DELETE FROM Series WHERE "
                         "rowid = %d" % series.rowid)

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
    global COMPACT_LIST

    DATABASE_NAME = config.get('config', 'database_name', fallback='manga.db')
    VOLUME_LIMIT = config.getint('config', 'volume_limit', fallback=128)
    PAGINATED = config.getboolean('config', 'paginated', fallback=False)
    SERIES_PER_PAGE = config.getint('config', 'series_per_page', fallback=5)
    COMPACT_LIST = config.getboolean('config', 'compact_list', fallback=False)

    DATA_MGR = DatabaseManager(DATABASE_NAME, init_database)
    print_all_series(DATA_MGR)

    while True:
        user_input = input("[S]earch, [L]ist, [A]dd, [E]dit, "
                           "[R]emove, [O]ptions, E[x]it: ")

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

        # Remove
        if user_input in ('r', 'R'):
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
                
                remove_series = input("Remove series from database? (y/N/q): ")
                if remove_series in ('q', 'Q'):
                    break
                if remove_series in ('y', 'Y'):
                    remove_series = input("Are you sure? "
                                          "This cannot be undone. (y/N): ")
                    if remove_series in ('y', 'Y'):
                        remove_series_from_database(DATA_MGR, series)
                    break

                count += 1
                if count != len(entries):
                    print("Next Series:")

        # Options
        if user_input in ('o', 'O'):
            print("-- OPTIONS --")
            print("1. Change Database Name")
            print("2. Change Volume Limit")
            print("3. Change Series Displayed Per Page")
            print("4. Use Compact Descriptions")
            print("5. Reset to Default Settings")
            print("6. Clear Database")
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
                    pass

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
                
                # 4. Use compact descriptions when listing series
                elif option == 4:
                    use_compact_list = input("Use compact descriptions? (y/N): ")
                    if use_compact_list == 'y' or use_compact_list == 'Y':
                        config["config"]["compact_list"] = "1"
                        COMPACT_LIST = True
                        with open("config.ini", "w") as config_ini:
                            config.write(config_ini)
                    else:
                        config["config"]["compact_list"] = "0"
                        COMPACT_LIST = False
                        with open("config.ini", "w") as config_ini:
                            config.write(config_ini)
                    pass

                # 4. Reset to default
                elif option == 5:
                    default = input("Reset all settings to default? (y/N): ")
                    if default == 'y' or default == 'Y':
                        set_default_cfg("config.ini")

                # 5. Clear database (Does not prompt user for series)
                elif option == 6:
                    delete_database = input("Remove Database? "\
                                            "(will copy to {0}.bak) y/N: "
                                            .format(DATABASE_NAME))
                    if delete_database == 'y' or delete_database == 'Y':
                        os.rename(DATABASE_NAME, DATABASE_NAME+".bak")
                        DATA_MGR = DatabaseManager(False)

            except Exception:
                print("Failure, returning to main screen")

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
    print_all_series(data_mgr)
    os.remove("test.db")

if __name__ == "__main__":
    main()
