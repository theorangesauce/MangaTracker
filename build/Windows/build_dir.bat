pyinstaller --onefile ^
            --exclude-module email ^
            --exclude-module http ^
            --exclude-module PySide2.QtNetwork ^
            --exclude-module PySide2.QtQml ^
            --paths=../../src/ ^
            --name mangatracker.exe ../../src/__main__.py
