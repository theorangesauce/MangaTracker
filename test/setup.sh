#!/bin/bash
rm mangatracker_exec
cd ../build/Linux
./build_exe.sh
cp dist/mangatracker_exec ../../test/
