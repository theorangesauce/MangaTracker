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

# Allow __main__ to run CLI without PySide2 installed
try:
    from mangatracker_gui import gui_main
    pyside2_installed = True
except ImportError:
    pyside2_installed = False

    def gui_main():
        print("PySide2 not installed, starting CLI")
        main()


def start_cli():
    main()
    exit()


def start_gui():
    gui_main()
    exit()


def start_default():
    if Config().default_to_gui and pyside2_installed:
        start_gui()
    else:
        start_cli()


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    parser = argparse.ArgumentParser(prog="MangaTracker",
                                     description="Track a manga collection.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-g",
                       "--gui",
                       action="store_true",
                       help="Start GUI (Requires PySide2)")
    group.add_argument("-c",
                       "--cli",
                       action="store_true",
                       help="Start CLI")

    args = parser.parse_args()

    if args.gui:
        start_gui()
    if args.cli:
        start_cli()

    start_default()
