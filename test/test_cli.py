""" test_series.py
Test file for series.py

Copyright 2020 by Nicholas Bishop
"""

import unittest
import os
import subprocess
import re

# set constants based on OS
if os.name == "nt":
    SETUPSCRIPT = "setup.bat"
    EXECUTABLE = "mangatracker.exe"
else:
    SETUPSCRIPT = "./setup.sh"
    EXECUTABLE = "./mangatracker_exec"

class CliTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(CliTest, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        print(cls)
        os.system("%s" % SETUPSCRIPT)
        os.system("%s -c < input/init.txt > out/init.txt" % EXECUTABLE)
        print("Initialized!")

    @classmethod
    def tearDownClass(cls):
        for file in ["config.ini", "manga.db", EXECUTABLE]:
            try:
                os.remove(file)
            except OSError:
                pass

    def testInitList(self):
        """Testing that initial series list is correct"""
        output = subprocess.check_output(
            ["%s" % EXECUTABLE, "-c"],
            universal_newlines=True,
            input="x\n")

        with open("expected/init.txt", 'r') as expected:
            series = [line.strip() for line in expected
                      if line[0:2] == "  " and
                      line.strip() != ""]

            pattern = ""
            for item in series:
                # matches series with name 'item'
                pattern += r"-{40}\n%s(.*\n)*" % item
            # matches last separator
            pattern += r"-{40}\n\["

            self.assertEqual(regexp(pattern, output), True)

    def testSearch(self):
        """Test search function with title, author, publisher"""
        output = run_input_sequence("input/search.txt")

        with open("out/search.txt", 'w') as search_out:
            search_out.write(output)

        test_cases = []

        with open("expected/search.txt", 'r') as expected:
            last_key = ""
            results = []
            for line in expected:
                if line.rstrip() == line.strip():
                    if last_key != "":
                        pair = (last_key, results)
                        test_cases.append(pair)

                    last_key = line.rstrip()
                    results = []
                elif line.strip() != "":
                    results.append(line.strip())

        sections = output.split("[S]earch, [L]ist, [A]dd, [E]dit, "
                                "[R]emove, [O]ptions, E[x]it:")
        sections.pop(0)

        patterns = []
        for pair in test_cases:
            # Search Term + num matches
            pattern = (r"Found %d entries for '%s':\n"
                       % (len(pair[1]), pair[0]))
            for item in pair[1]:
                # matches series with name 'item'
                pattern += r"-{40}\n%s(.*\n)*" % item
            # matches last separator
            pattern += r"-{40}\n"

        for section in sections:
            if len(patterns) and regexp(patterns[0], section):
                patterns.pop(0)

        self.assertEqual(regexp(pattern, output), True)

    def testList(self):
        """Test different list functions

        Runs each function in the list submenu with 'show empty
        series' disabled and enabled

        """
        output = run_input_sequence("input/list.txt")

        test_cases = []

        with open("out/list.txt", 'w') as list_out:
            list_out.write(output)

        with open("expected/list.txt", 'r') as expected:
            last_key = ""
            last_case = ""
            cases = []
            results = []
            for line in expected:
                if line.strip() == "":
                    continue

                if line.rstrip() == line.strip():
                    if last_key != "":
                        if last_case != "":
                            pair = (last_case, results)
                            cases.append(pair)
                        pair = (last_key, cases)
                        test_cases.append(pair)

                    last_key = line.rstrip()
                    last_case = ""
                    cases = []
                    results = []

                elif line[2:].rstrip() == line.strip():
                    if last_case != "":
                        pair = (last_case, results)
                        cases.append(pair)

                    last_case = line.strip()
                    results = []

                elif line.strip() != "":
                    results.append(line.strip())

            if last_key != "":
                if last_case != "":
                    pair = (last_case, results)
                    cases.append(pair)
                pair = (last_key, cases)
                test_cases.append(pair)

        # for case in test_cases:
        #     print(case[0])
        #     for subcase in case[1]:
        #         print(subcase)
        #     print()

        patterns = []
        sections = output.split("[S]earch, [L]ist, [A]dd, [E]dit, "
                                "[R]emove, [O]ptions, E[x]it:")

        # remove initial series list when program starts
        sections.pop(0)
        for case in test_cases[0][1]:
            pattern = ""
            for item in case[1]:
                # matches series with name 'item'
                pattern += r"-{40}\n%s(.*\n)*" % item
            # matches last separator
            pattern += r"-{40}\n"
            patterns.append(pattern)

        pattern = r"Showing series without any volumes in lists"
        patterns.append(pattern)

        for case in test_cases[1][1]:
            pattern = ""
            for item in case[1]:
                # matches series with name 'item'
                pattern += r"-{40}\n%s(.*\n)*" % item
            # matches last separator
            pattern += r"-{40}\n"
            patterns.append(pattern)

        for section in sections:
            if len(patterns) and regexp(patterns[0], section):
                patterns.pop(0)

        self.assertEqual(len(patterns), 0)

    def testAddRemove(self):
        """Tests add and remove submenus"""
        output = run_input_sequence("input/add-remove.txt")

        with open("out/add-remove.txt", 'w') as ar_out:
            ar_out.write(output)

        test_cases = []

        with open("expected/add-remove.txt") as expected:
            last_key = ""
            last_case = ""
            cases = []
            results = []
            for line in expected:
                if line.strip() == "":
                    continue

                if line.rstrip() == line.strip():
                    if last_key != "":
                        if last_case != "":
                            pair = (last_case, results)
                            cases.append(pair)
                        pair = (last_key, cases)
                        test_cases.append(pair)

                    last_key = line.rstrip()
                    last_case = ""
                    cases = []
                    results = []

                elif line[2:].rstrip() == line.strip():
                    if last_case != "":
                        pair = (last_case, results)
                        cases.append(pair)

                    last_case = line.strip()
                    results = []

                elif line.strip() != "":
                    results.append(line.strip())

            if last_key != "":
                if last_case != "":
                    pair = (last_case, results)
                    cases.append(pair)
                pair = (last_key, cases)
                test_cases.append(pair)

        patterns = []
        sections = output.split("[S]earch, [L]ist, [A]dd, [E]dit, "
                                "[R]emove, [O]ptions, E[x]it:")
        # remove initial series list when program starts
        sections.pop(0)
        for case in test_cases[0][1]:
            pattern = ""
            for item in case[1]:
                # matches series with name 'item'
                pattern += r"-{40}\n%s(.*\n)*" % item
            # matches last separator
            pattern += r"-{40}\n"
            patterns.append(pattern)

        patterns.append(r"Series .* removed from database.")

        for case in test_cases[1][1]:
            pattern = ""
            for item in case[1]:
                # matches series with name 'item'
                pattern += r"-{40}\n%s(.*\n)*" % item
            # matches last separator
            pattern += r"-{40}\n"
            patterns.append(pattern)

        for section in sections:
            if len(patterns) and regexp(patterns[0], section):
                patterns.pop(0)

        if len(patterns):
            for pattern in patterns:
                print(pattern + " not matched!")

        self.assertEqual(len(patterns), 0)


def run_input_sequence(infilename):
    """Runs the given executable with the given list of inputs"""
    with open(infilename, 'r') as infile:
        return subprocess.check_output(
            ["%s" % EXECUTABLE, "-c"],
            universal_newlines=True,
            stdin=infile)


def regexp(pattern, value):
    """
    regexp()
    Simple regex function

    Arguments:
    pattern - regex to filter with
    value   - string to search with regex
    """
    reg = re.compile(pattern)
    return reg.search(value) is not None
