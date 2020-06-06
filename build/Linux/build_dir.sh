#!/bin/bash
pyinstaller --onedir --noconfirm --noupx \
            --exclude-module email \
            --exclude-module http \
            --exclude-module PySide2.QtNetwork \
            --exclude-module PySide2.QtQml \
            --paths="../../src/" \
            --name mangatracker \
            ../../src/__main__.py;
