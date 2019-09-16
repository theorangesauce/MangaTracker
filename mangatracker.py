#!/usr/bin/env python3
""" mangatracker.py
Program to track owned and desired manga series.
Run using ./mangatracker.py
"""
import os.path
from databasemanager import DatabaseManager
from databasemanager import regexp
from series import *
from config import Config

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
        if (config.series_per_page != 0
            and count != 0
            and count % config.series_per_page == 0
        ):
            print("----------------------------------------")
            continue_print = input("Press Enter to continue "
                                   "or type 'q' to stop: ")
            if continue_print in ('q', 'Q'):
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
        if (config.series_per_page != 0
            and count != 0
            and count % config.series_per_page == 0
        ):
            print("----------------------------------------")
            continue_print = input("Press Enter to continue "
                                   "or type 'q' to stop: ")
            if continue_print in ('q', 'Q'):
                return

        print("----------------------------------------")
        series = entry_to_series(entry)
        print(series)
        count += 1

    if len(entries) > 0:
        print("----------------------------------------")

def list_series(data_mgr):
    """
    list_series()

    Lists all series from the database which meet user-specified criteria
    """
    selection = input("List [A]ll / [C]omplete / "
                      "[I]ncomplete / Series with [G]aps: ")
    config = Config()

    # Completed Series
    if selection in ('c', 'C'):
        cur = data_mgr.query("SELECT rowid, * FROM Series WHERE "
                             "is_completed = 1 ORDER BY name")
        entries = cur.fetchall()

        if len(entries) == 0:
            print("No completed series found.")
            return

        print("Found {0} completed series:".format(len(entries)))
        print_entries_list(entries)

    # Incomplete Series
    elif selection in ('i', 'I'):
        cur = data_mgr.query("SELECT rowid, * FROM Series WHERE "
                             "is_completed = 0 ORDER BY name")
        entries = cur.fetchall()

        if len(entries) == 0:
            print("No incomplete series found.")
            return

        print("Found {0} incomplete series:".format(len(entries)))
        print_entries_list(entries)

    # Series with Gaps
    elif selection in ('g', 'G'):
        list_series_with_gaps(data_mgr, config)

    # Default (print all)
    else:
        print_all_series(data_mgr)

def list_series_with_gaps(data_mgr, config):
    """
    list_series_with_gaps()
    Retrieves and prints the list of all series in the database
    for which there is a gap (the set of all volumes is not continuous)

    Arguments:
    data_mgr - DatabaseManager object with active connection to database
    config - Config object with current config settings loaded.
    """
    cur = data_mgr.query("SELECT rowid, * FROM Series ORDER BY name")
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
        if (config.series_per_page != 0
            and count != 0
            and count % config.series_per_page == 0
        ):
            print("----------------------------------------")
            continue_print = input("Press Enter to continue "
                                   "or type 'q' to stop: ")
            if continue_print in ('q', 'Q'):
                return

        print("----------------------------------------")
        print(series)
        #print("----------------------------------------")
        count += 1

    if len(series_with_gaps) > 0:
        print("----------------------------------------")


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
    data_mgr.query("DELETE FROM Series WHERE "
                   "rowid = %d" % series.rowid)

def main():
    """
    main()
    Main driver function for mangatracker program
    """
    config = Config()
    data_mgr = DatabaseManager(config.database_name, init_database)

    print_all_series(data_mgr)

    while True:
        user_input = input("[S]earch, [L]ist, [A]dd, [E]dit, "
                           "[R]emove, [O]ptions, E[x]it: ")

        if user_input in ('x', 'X'):
            break

        if user_input in ('s', 'S'):
            # TODO: color matching text (maybe not?)
            entries, search_term = search_for_series(data_mgr)

            print()
            if len(entries) == 0:
                print("No series found for '{0}'."
                      .format(search_term))
                continue

            print("Found {0} entries for '{1}':"
                  .format(len(entries), search_term))
            print_entries_list(entries)
            continue

        if user_input in ('l', 'L'):
            list_series(data_mgr)

        # Add Series
        if user_input in ('a', 'A'):
            try:
                new_series = input_series(data_mgr)
            except KeyboardInterrupt:
                print("\nAdd series operation cancelled")
                new_series = None

            if new_series is not None:
                new_series.add_series_to_database(data_mgr)
                print("----------------------------------------")
                print(new_series)
                print("----------------------------------------")

            continue

        # Edit Series
        if user_input in ('e', 'E'):
            edit_series(data_mgr)

        # Remove
        if user_input in ('r', 'R'):
            remove_series(data_mgr)

        # Options
        if user_input in ('o', 'O'):
            options_menu(config)
            # Reset database connection if name changed or database deleted
            data_mgr = DatabaseManager(config.database_name, None)

def edit_series(data_mgr):
    """
    edit_series()
    Retrieves a list of potential series to edit based on
    user input, and iterates through the list until the user
    selects one to edit.

    Arguments:
    data_mgr - DatabaseManager object connected to active database
    """
    entries, search_term = search_for_series(data_mgr)
    count = 0

    print()
    if len(entries) == 0:
        print("No series found for '{0}'."
              .format(search_term))
        return

    print("Found {0} entries for '{1}':"
          .format(len(entries), search_term))

    for entry in entries:
        print("----------------------------------------")
        series = entry_to_series(entry)
        print(series)
        print("----------------------------------------")

        found_series = input("Edit this series? (y/N/q): ")
        if found_series in ('q', 'Q'):
            break
        if found_series in ('y', 'Y'):
            series.edit(data_mgr)
            break

        count += 1
        if count != len(entries):
            print("Next Series:")

def remove_series(data_mgr):
    """
    remove_series()
    Allows user to select a series to remove from the database

    Arguments:
    data_mgr - DatabaseManager object connected to current database
    """
    entries, search_term = search_for_series(data_mgr)
    count = 0

    print()
    if len(entries) == 0:
        print("No series found for '{0}'."
              .format(search_term))
        return

    print("Found {0} entries for '{1}':"
          .format(len(entries), search_term))

    for entry in entries:
        print("----------------------------------------")
        series = entry_to_series(entry)
        print(series)
        print("----------------------------------------")

        remove = input("Remove series from database? (y/N/q): ")
        if remove in ('q', 'Q'):
            break
        if remove in ('y', 'Y'):
            remove = input("Are you sure? "
                                  "This cannot be undone. (y/N): ")
            if remove in ('y', 'Y'):
                remove_series_from_database(data_mgr, series)
            break

        count += 1
        if count != len(entries):
            print("Next Series:")

def options_menu(config):
    """
    options_menu()
    Change config options for MangaTracker
    Options:
    1. Change name of database file (default manga.db)
    2. Change the maximum number of volumes allowed
       per series (default 128)
    3. Change number of series displayed per page (default 0)
    4. Select either verbose descriptions or
       1-line descriptions (default verbose)
    5. Reset all settings to default

    Arguments:
    data_mgr - DatabaseManager object connected to current database
    config - Config object with current config settings loaded
    """
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
            if new_db_name != "" and not os.path.exists(new_db_name):
                config.set_property("database_name", new_db_name)
            else:
                print("Database name not changed.")

        # 2. Change volume limit
        elif option == 2:
            new_vol_limit = input("Enter new volume limit"
                                  "(Must be multiple of 32): ")
            new_vol_limit = int(new_vol_limit)
            if new_vol_limit % 32 == 0 and new_vol_limit >= 32:
                config.set_property("volume_limit", new_vol_limit)
            else:
                print("Invalid volume limit, not changed.")

        # 3. Change series per page ( 0 for no limit)
        elif option == 3:
            new_series_per_page = input("Enter maximum number of "
                                        "series to display per page, "
                                        "or 0 to not use pages: ")
            if new_series_per_page == '0':
                config.set_property("series_per_page", 0)
            else:
                try:
                    new_series_per_page = int(new_series_per_page)
                    if new_series_per_page < 1:
                        print("Series per page must be greater than 1")
                    else:
                        config.set_property("series_per_page",
                                            new_series_per_page)
                except (ValueError, TypeError):
                    pass

        # 4. Use compact descriptions when listing series
        elif option == 4:
            use_compact_list = input("Use compact descriptions? (y/N): ")
            if use_compact_list in ('y', 'Y'):
                config.set_property("compact_list", True)
            else:
                config.set_property("compact_list", False)

        # 5. Reset to default
        elif option == 5:
            default = input("Reset all settings to default? (y/N): ")
            if default in ('y', 'Y'):
                config.set_default_config("config.ini")

        # 6. Clear database (Does not prompt user for series)
        elif option == 6:
            delete_database = input("Remove Database? "
                                    "(will copy to {0}.bak) y/N: "
                                    .format(config.database_name))
            if delete_database in ('y', 'Y'):
                os.rename(config.database_name,
                          config.database_name+".bak")
                DatabaseManager(False, init_database)

        else:
            print("Invalid option, returning to main screen")

    except ValueError:
        print("Invalid option, returning to main screen")

if __name__ == "__main__":
    main()
