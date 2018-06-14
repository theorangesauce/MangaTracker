# MangaTracker
# Program to track owned and desired manga series

import sqlite3 as lite
import os.path
import math

# Global constants
DATABASE_NAME = "manga.db"
VOLUME_LIMIT = 128
PAGINATED = False
    
class DatabaseManager(object):
    """
    DatabaseManager(object)
    Main interface between program and SQLite3 database
    """
    def __init__(self, new_db_needed=False):
        self.con = lite.connect(DATABASE_NAME)
        self.cur = self.con.cursor()
        self.query("SELECT name FROM sqlite_master \
                    WHERE type='table' AND name='Series'")
        if self.cur.fetchone() == None: 
            self.query("CREATE TABLE Series(name TEXT, volumes_owned TEXT, \
                        is_completed INT, next_volume INT)")
            next_series = input_series(self)
            while next_series != None:
                self.query("INSERT INTO Series VALUES('{0}','{1}',{2},{3})"
                           .format(
                    next_series.name,
                    next_series.volumes_owned,
                    next_series.is_completed,
                    next_series.get_next_volume()))
                print(next_series)
                next_series = input_series(self)
    
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
    def __init__(self, name, volumes_owned, is_completed, next_volume=-1):
        self.name = name
        self.volumes_owned = volumes_owned
        self.is_completed = is_completed
        self.next_volume = next_volume
        
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
                if num != 0:
                    none_owned = 0
                if num == 0: # no need to check empty set
                    if first != -1:
                        last = index * 32
                        self.volumes_owned_readable += (
                            "{0}, ".format(first) if first == last
                            else "{0}-{1}, ".format(first, last))
                        first = -1
                    index += 1
                    continue
                for i in range(0, 32):
                    #print("i: {0}, first: {1}".format(i, first))
                    if first == -1 and num & (1 << i) != 0: # assuming sequential 
                        first = index * 32 + i + 1
                    if first != -1 and num & (1 << i) == 0:
                        last = index * 32 + i
                        self.volumes_owned_readable += (
                            "{0}, ".format(first) if first == last
                            else "{0}-{1}, ".format(first, last))
                        first = -1
                index += 1
            if none_owned:
                self.volumes_owned_readable = "None"
            else:
                self.volumes_owned_readable = self.volumes_owned_readable[:-2]
        return self.volumes_owned_readable

    def get_name(self):
        return self.name

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

    def update_database_entry(self, data_mgr):
        """
        update_database_entry()
        sync series with database; open connection to database within function
        (should pass db connection as function argument?)
        """
        return
    
    def __str__(self):
        result = (self.name + ": " + self.get_volumes_owned() +
              " (Completed: " + self.get_is_completed() + ")\n" + 
              "Next Volume: %d" % self.get_next_volume())
        return result

def print_database(data_mgr):
    """
    print_database(data_mgr)
    Print status of all series in 
    """
    cur = data_mgr.query("SELECT * FROM Series")
    entries = cur.fetchall()
    for entry in entries:
        # TODO: convert entries to Series() objects
        print(entry)
        series = Series(entry[0], entry[1], entry[2], entry[3])
        print(series)

def input_series(data_mgr):
    """
    input_series():
    Gets values for the name of a manga series, volumes currently owned,
    and whether the series is completed
    """
    series_name = input("Enter manga name or leave blank to cancel: ")
    if series_name == "":
        return None
    # try:
    cur = data_mgr.query("Select name FROM Series WHERE name = '{0}'"
                         .format(series_name))
    row = cur.fetchall()
    if len(row) > 0: # TODO: check database for name
        print("Name already in database!")
        return None
    # except:
    #     print("Database query failed, continuing...")
    volumes_raw = input("Enter volumes owned (if any) (ex. 1, 3-5): ")
    volumes_owned = generate_volumes_owned(volumes_raw)

    is_completed = input("Is this series completed? (y/N): ")
    if is_completed != 'y' and is_completed != 'Y':
        is_completed = 0
    else:
        is_completed = 1

    return Series(series_name, volumes_owned, is_completed)

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
                print("Start volume must be greater than zero; \
                       token %s ignored" % num)
                continue
            if nums[1] > VOLUME_LIMIT:
                print("End volume too high; consider raising volume limit \
                       (currently {0})".format(VOLUME_LIMIT))
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
                print("Token {0} ignored; volume number must be \
                       greater than zero".format(num))
                continue
            if num >= VOLUME_LIMIT:
                print("Token {0} ignored; volume number must be lower \
                       than volume limit (currently {1})"
                      .format(num, VOLUME_LIMIT))
                continue
            vol_arr[num // 32] |= 1 << (num % 32)
    result = ""
    for num in vol_arr:
        result += format(num) + ','
    return result[:-1]

def main():
    """
    main()
    Main driver function for mangatracker program
    """
    DATA_MGR = DatabaseManager()
    print_database(DATA_MGR)
    while True:
        user_input = input("[S]earch, [L]ist, [A]dd, [O]ptions, E[x]it: ")
        if user_input == 'x' or user_input == 'X':
            break
        if user_input == 's' or user_input == 'S':
            print("Search goes here!")
            # TODO: allow user to search for a specific series, modify/delete
            #   entries, etc.
        if user_input == 'l' or user_input == 'L':
            print_database(DATA_MGR)
        if user_input == 'a' or user_input == 'A':
            new_series = input_series(DATA_MGR)
            if(new_series != None):
                DATA_MGR.query(
                    "INSERT INTO Series VALUES('{0}','{1}',{2},{3})".format(
                        new_series.name,
                        new_series.volumes_owned,
                        new_series.is_completed,
                        new_series.get_next_volume()))
        if user_input == 'o' or user_input == 'O':
            print("Options go here!")
            # TODO: allow user to control settings (modify vol limit, delete
            #   database, etc.

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
