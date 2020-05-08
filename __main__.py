#!/usr/bin/env python3
"""__main__.py

Start mangatracker program using command line arguments
Copyright 2020 by Nicholas Bishop

"""

import argparse
import os
from sys import exit
from config import Config
from mangatracker import main
from mangatracker_gui import gui_main

def start_cli():
    main()
    exit()

def start_gui():
    gui_main()
    exit()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    parser = argparse.ArgumentParser(prog="MangaTracker", description="Track a manga collection.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-g", "--gui", action="store_true", help="Start GUI")
    group.add_argument("-c", "--cli", action="store_true", help="Start CLI")

    args = parser.parse_args()

    if args.gui:
        start_gui()
    if args.cli or not Config().default_to_gui:
        start_cli()

    start_gui()
