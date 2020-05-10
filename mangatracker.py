#!/usr/bin/env python3
""" mangatracker.py
Program to track owned and desired manga series.
Run using ./mangatracker.py

Copyright 2019 by Nicholas Bishop
"""
import os.path
from databasemanager import DatabaseManager
from databasemanager import regexp
from databasemanager import is_database
from series import Series
from series import SeriesItems as SI
from series import input_series
from series import init_database
from config import Config

def entry_to_series(entry):
    """
    entry_to_series()
    Takes a single row from a database query and converts it
    into a series.
    """
    if not entry:
        return None
    
    series = Series(name=str(entry[SI.NAME]),                # Series Name
                    volumes_owned=str(entry[SI.VOL_OWNED]),  # Volumes Owned
                    is_completed=entry[SI.IS_COMPLETED],     # Is Completed
                    next_volume=entry[SI.NEXT_VOLUME],       # Next Volume
                    publisher=str(entry[SI.PUBLISHER]),      # Publisher
                    author=str(entry[SI.AUTHOR]),            # Author
                    alt_names=str(entry[SI.ALT_NAMES]),      # Alternate Names
                    rowid=entry[SI.ROWID])                   # Row ID
                                                             # (for updates)
    return series


def print_all_series(data_mgr, order="name"):
    """
    print_all_series(data_mgr)
    Print status of all series in database
    """
    cur = data_mgr.query("SELECT rowid, * FROM Series ORDER BY %s" % (order))
    entries = cur.fetchall()
    unknown_entries = []
    count = 0
    config = Config()

    for entry in entries:
        if entry[SI[order.upper()]] == "Unknown":
            unknown_entries.append(entry)
            continue
        if not config.show_empty_series and entry[SI.VOL_OWNED] == "0,0,0,0":
            continue
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

    if unknown_entries:
        for entry in unknown_entries:
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

    if entries:
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

    if entries:
        print("----------------------------------------")


def list_series(data_mgr):
    """
    list_series()

    Lists all series from the database which meet user-specified criteria
    """
    selection = input("List [A]ll / by [O]ther Field / [C]omplete / "
                      "[I]ncomplete / with [G]aps / [W]ishlist: ")
    config = Config()

    # Completed Series
    if selection in ('c', 'C'):
        cur = data_mgr.query("SELECT rowid, * FROM Series WHERE "
                             "is_completed = 1 ORDER BY name")
        entries = cur.fetchall()

        if not entries:
            print("No completed series found.")
            return

        if not config.show_empty_series:
            for entry in entries:
                if entry[SI["VOL_OWNED"]] == "0,0,0,0":
                    entries.remove(entry)

        print("Found {0} completed series:".format(len(entries)))
        print_entries_list(entries)

    # Incomplete Series
    elif selection in ('i', 'I'):
        cur = data_mgr.query("SELECT rowid, * FROM Series WHERE "
                             "is_completed = 0 ORDER BY name")
        entries = cur.fetchall()

        if not entries:
            print("No incomplete series found.")
            return

        if not config.show_empty_series:
            for entry in entries:
                if entry[SI["VOL_OWNED"]] == "0,0,0,0":
                    entries.remove(entry)

        print("Found {0} incomplete series:".format(len(entries)))
        print_entries_list(entries)

    # Series with Gaps
    elif selection in ('g', 'G'):
        list_series_with_gaps(data_mgr, config)

    # Order by another field
    elif selection in ('o', 'O'):
        list_series_by_field(data_mgr)

    # View Wishlist (all empty series)
    elif selection in ('w', 'W'):
        cur = data_mgr.query("SELECT rowid, * FROM Series WHERE "
                             "volumes_owned = '0,0,0,0'")
        entries = cur.fetchall()

        if not entries:
            print("No wishlisted series found.")
            return

        print("Found {0} wishlisted series:".format(len(entries)))
        print_entries_list(entries)

    # Default (print all)
    else:
        print_all_series(data_mgr)


def list_series_by_field(data_mgr):
    """
    list_series_by_field()

    List items ordered by a specific field when listing all series.

    Arguments:
    data_mgr - DatabaseManager object used for interfacing with database
    """
    selection = input("Sort by [N]ame / [A]uthor / [P]ublisher: ")
    if selection in ('a', 'A'):
        print_all_series(data_mgr, "author")
    elif selection in ('p', 'P'):
        print_all_series(data_mgr, "publisher")
    else:
        print_all_series(data_mgr, "name")

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

    if not series_with_gaps:
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
        count += 1

    if series_with_gaps:
        print("----------------------------------------")


def search_for_series(data_mgr):
    """
    search_for_series()
    Takes a DatabaseManager object, queries the database for a
    search term given by user, returns the search term and
    any matching entries
    """
    search_term = input("Search for series by name or other field: ")
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
    print("Series '%s' removed from database." % (series.name))


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
            if not entries:
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
            data_mgr = DatabaseManager(config.database_name, init_database, False)


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
    if not entries:
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
            if series.edit(data_mgr):
                delete_confirm = input("Are you sure you want to remove %s? "
                                       "This cannot be undone. (y/N): "
                                       % (series.name))
                if delete_confirm in ('y', 'Y'):
                    remove_series_from_database(data_mgr, series)
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
    if not entries:
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
    5. Show empty series in normal lists (default False)
    6. Open GUI or CLI by default (default GUI)
    7. Reset all settings to default
    8. Clear database

    Arguments:
    data_mgr - DatabaseManager object connected to current database
    config - Config object with current config settings loaded
    """
    print("-- OPTIONS --\n"
          "1. Change Database Name\n"
          "2. Change Volume Limit\n"
          "3. Change Series Displayed Per Page\n"
          "4. Use Compact Descriptions\n"
          "5. Show Empty Series in Lists\n"
          "6. Choose whether CLI or GUI opens by default\n"
          "7. Reset to Default Settings\n"
          "8. Clear Database")
    option = input("Enter a number to modify option: ")
    try:
        option = int(option)
        # 1. Change database name
        if option == 1:
            new_db_name = input("Enter new database name, or leave "
                                "blank to leave unchanged: ")
            if (new_db_name != "" and new_db_name != config.database_name
                    and is_database(new_db_name)
               ):
                config.set_property("database_name", new_db_name)
                print("Database changed to %s." % new_db_name)
            else:
                print("Database name not changed.")

        # 2. Change volume limit
        elif option == 2:
            new_vol_limit = input("Enter new volume limit"
                                  "(Must be multiple of 32): ")
            new_vol_limit = int(new_vol_limit)
            if new_vol_limit % 32 == 0 and new_vol_limit >= 32:
                config.set_property("volume_limit", new_vol_limit)
                print("Volume limit changed to %d." % new_vol_limit)
            else:
                print("Invalid volume limit, not changed.")

        # 3. Change series per page ( 0 for no limit)
        elif option == 3:
            new_series_per_page = input("Enter maximum number of "
                                        "series to display per page, "
                                        "or 0 to not use pages: ")
            if new_series_per_page == '0':
                config.set_property("series_per_page", 0)
                print("Program will not use pages.")
            else:
                try:
                    new_series_per_page = int(new_series_per_page)
                    if new_series_per_page < 1:
                        print("Series displayed per page must be greater than or equal to 1.")
                    else:
                        config.set_property("series_per_page",
                                            new_series_per_page)
                        print("Series displayed per page set to %d." % new_series_per_page)
                except (ValueError, TypeError):
                    print("Invalid value, series per page not changed.")

        # 4. Use compact descriptions when listing series
        elif option == 4:
            use_compact_list = input("Use compact descriptions? (y/N): ")
            if use_compact_list in ('y', 'Y'):
                config.set_property("compact_list", True)
                print("Using compact descriptions.")
            else:
                config.set_property("compact_list", False)
                print("Using full descriptions.")

        # 5. Show empty series in normal lists
        elif option == 5:
            show_empty_series = input("Show series without any volumes in lists? (y/N): ")
            if show_empty_series in ('y', 'Y'):
                config.set_property("show_empty_series", True)
                print("Showing series without any volumes in lists.")
            else:
                config.set_property("show_empty_series", False)
                print("Hiding series without any volumes from lists.")

        # 6. Choose whether CLI or GUI opens by default
        elif option == 6:
            default_to_cli = input("Open CLI by default when no "
                                   "command-line options provided? (y/N): ")
            if default_to_cli in ('y', 'Y'):
                config.set_property("default_to_gui", False)
                print("Program will default to CLI when no arguments are provided.")
            else:
                config.set_property("default_to_gui", True)
                print("Program will default to GUI when no arguments are provided.")

        # 7. Reset to default
        elif option == 7:
            default = input("Reset all settings to default? (y/N): ")
            if default in ('y', 'Y'):
                config.set_default_config("config.ini")
                print("Settings reset to default.")
            else:
                print("Settings not changed.")

        # 8. Clear database (Does not prompt user for series)
        elif option == 8:
            delete_database = input("Remove Database? "
                                    "(will copy to {0}.bak) y/N: "
                                    .format(config.database_name))
            if delete_database in ('y', 'Y'):
                os.rename(config.database_name,
                          config.database_name+".bak")
                print("Database deleted; initializing new database...")
                DatabaseManager(False, init_database)
            print("Database not changed.")

        else:
            print("Invalid option, returning to main screen")

    # int(option) fails
    except ValueError:
        print("Invalid option, returning to main screen")


if __name__ == "__main__":
    main()
