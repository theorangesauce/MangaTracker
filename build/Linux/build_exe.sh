#!/bin/bash
pyinstaller --onefile --noupx \
            --exclude-module email \
            --exclude-module http \
            --exclude-module PySide2.QtNetwork \
            --exclude-module PySide2.QtQml \
            --paths="../../src/" \
            --name mangatracker_exec \
            ../../src/__main__.py;
