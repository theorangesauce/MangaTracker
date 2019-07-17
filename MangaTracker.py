#!/usr/bin/env python3
# MangaTracker
# Program to track owned and desired manga series

import os
import math
import configparser
from DatabaseManager import *
from Series import *
from Config import Config

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
    series = Series(name=str(entry[1]),          # Series Name
                    volumes_owned=str(entry[2]), # Volumes Owned
                    is_completed=entry[3],       # Is Completed
                    next_volume=entry[4],        # Next Volume
                    publisher=str(entry[5]),     # Publisher
                    author=str(entry[6]),        # Author
                    alt_names=str(entry[7]),     # Alternate Names
                    rowid=entry[0])              # Row ID (for updates)
    return series

def print_all_series(data_mgr):
    """
    print_all_series(data_mgr)
    Print status of all series in database
    """
    cur = data_mgr.query("SELECT rowid, * FROM Series ORDER BY name")
    entries = cur.fetchall()
    count = 0
    config = Config()

    for entry in entries:
        if (config.paginated and count != 0 
            and count % config.series_per_page == 0):
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

def print_entries_list(entries):
    """
    print_entries_list()
    Function to print all items matching database query
    """
    count = 0
    config = Config()

    for entry in entries:
        if (config.paginated and count != 0 
            and count % config.series_per_page == 0):
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
    """
    list_series()

    Lists all series from the database which meet user-specified criteria
    """
    selection = input("List [A]ll / [C]omplete / "
                      "[I]ncomplete / Series with [G]aps: ")
    config = Config()

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
            if (config.paginated and count != 0 
                and count % config.series_per_page == 0):
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
    config = Config()
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
                # 1. Change database name
                if option == 1:
                    new_db_name = input("Enter new database name, or leave "\
                                        "blank to leave unchanged: ")
                    if new_db_name != "" and not os.exists(new_db_name):
                        config.set_property("database_name", new_db_name)
                    else:
                        print("Database name not changed.")
                    pass

                # 2. Change volume limit
                elif option == 2:
                    new_vol_limit = input("Enter new volume limit"
                                          "(Must be multiple of 32): ")
                    new_vol_limit = int(new_vol_limit)
                    if new_vol_limit % 32 == 0 and new_vol_limit >= 32:
                        config.set_property("volume_limit", new_vol_limit)
                    else:
                        print("Invalid volume limit, not changed.")
                    pass

                # 3. Change series per page ( 0 for no limit)
                elif option == 3:
                    new_series_per_page = input("Enter maximum number of "
                                                "series to display per page, "
                                                "or 0 to not use pages: ")
                    if new_series_per_page == '0':
                        config.set_property("paginated", False)
                    try:
                        new_series_per_page = int(new_series_per_page)
                        if new_series_per_page < 1:
                            print("Series per page must be greater than 1!")
                        else:
                            config.set_property("series_per_page", 
                                                new_series_per_page)
                            config.set_property("paginated", True)
                    except (ValueError, TypeError):
                        pass
                
                # 4. Use compact descriptions when listing series
                elif option == 4:
                    use_compact_list = input("Use compact descriptions? (y/N): ")
                    if use_compact_list == 'y' or use_compact_list == 'Y':
                        config.set_property("compact_list", True)
                    else:
                        config.set_property("compact_list", False)

                # 5. Reset to default
                elif option == 5:
                    default = input("Reset all settings to default? (y/N): ")
                    if default == 'y' or default == 'Y':
                        config.set_default_cfg("config.ini")

                # 6. Clear database (Does not prompt user for series)
                elif option == 6:
                    delete_database = input("Remove Database? "
                                            "(will copy to {0}.bak) y/N: "
                                            .format(DATABASE_NAME))
                    if delete_database == 'y' or delete_database == 'Y':
                        os.rename(DATABASE_NAME, DATABASE_NAME+".bak")
                        DATA_MGR = DatabaseManager(False)
                
                else:
                    print("Invalid option, returning to main screen")
                    pass

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
