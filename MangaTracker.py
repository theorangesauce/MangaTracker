# MangaTracker
# Program to track owned and desired manga series

import sqlite3 as lite
import os.path
import math

DATABASE_NAME = "manga.db"
VOLUME_LIMIT = 128
CON = None

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

    def get_volumes_owned():
        """
        get_volumes_owned()
        Inverse of generate function; convert integers into human-readable
        format (same as original input format
        """
        return

    def get_name():
        return self.name

    def get_completed_status():
        return self.is_completed

    def get_next_volume():
        # check if calculated, otherwise return current value
        if self.next_volume < 0:
            self.next_volume = calculate_next_volume()
        return self.next_volume


    def calculate_next_volume():
        index = 0
        for num in self.vol_arr:
            for i in range(0, 32):
                if num & (1 << i) == 0:
                    return index * 32 + i + 1
            index += 1
        print("Next volume for %s would exceed volume limit" % self.name)
        return index * 32 + 1

    def update_database_entry():
        """
        update_database_entry()
        sync series with database; open connection to database within function
        (should pass db connection as function argument?)
        """
        return

def retrieve_series_from_database():
    return

def main():
    """
    main()
    Main driver function for mangatracker program
    """

    return

def input_series():
    """
    input_series():
    Gets values for the name of a manga series, volumes currently owned,
    and whether the series is completed
    """
    series_name = input("Enter manga name or leave blank to cancel: ")
    if series_name == "":
        return
    if series_name == "": # TODO: check database for name
        print("Name already in database!")

    volumes_raw = input("Enter volumes owned (if any) (ex. 1, 3-5): ")
    volumes_owned = generate_volumes_owned(volumes_raw)

    is_completed = input("Is this series completed? (y/N): ")
    if is_completed != 'y':
        is_completed = 'n'

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
        if '-' in num:
            nums = [int(k) for k in num.split('-')] # should always have 2 integers
            if nums[0] < 1:
                print("Start volume must be greater than zero; token %s ignored" % num)
                continue
            if nums[1] > VOLUME_LIMIT:
                print("End volume too high; consider raising volume limit (currently %d)" % VOLUME_LIMIT)
                nums[1] = 128
            for i in range(nums[0]-1, nums[1]):
                print("ANDing volume %d" % i)
                vol_arr[i // 32] |= 1 << (i % 32)
        else:
            num = int(num) - 1
            if num < 0:
                print("Token %s ignored; volume number must be greater than zero" % num)
                continue
            if num >= VOLUME_LIMIT:
                print("Token %s ignored; volume number must be lower than volume limit (currently %d)" % VOLUME_LIMIT)
                continue
            print("ANDing volume %s" % (num))
            vol_arr[num // 32] |= 1 << (num % 32)
    print vol_arr
    # TODO: concat into string
    result = ""
    for num in vol_arr:
        result += format(num) + ','
    return result[:-1]
