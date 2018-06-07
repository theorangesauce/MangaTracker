# MangaTracker
# Program to track owned and desired manga series

import sqlite3 as lite
import os.path

DATABASE_NAME = "manga.db"
VOLUME_LIMIT = 128
CON = None

def input_series():
    """
    input_series():
    Gets values for the name of a manga series, volumes currently owned,
    and whether the series is completed
    """
    name = input("Enter manga name or leave blank to cancel: ")
    if name == "":
        return
    if name == "": #check database for name
        print("Name already in database!")
    volumes_owned = input("Enter volumes owned (if any) (ex. 1, 3-5): ")
    is_completed = input("Is this series completed? (y/N): ")

def generate_volumes_owned(str):
    """
    generate_volumes_owned(str):
    Takes a string of numbers in a comma-separated list (ex. "1, 3-5, 7"),
    stores them bitwise in 32-bit integers, then concatenates bitwise 
    representations of them in a string and returns the result
    """
    arr_length = VOLUME_LIMIT / 32
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
    #TODO: concat into string
