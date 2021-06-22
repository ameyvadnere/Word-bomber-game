#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This script converts a .py file to an executable or game installer.
# Run in the following manner: 
#   - python exec_maker.py build (for making an executable)
#   - python exec_maker.py bdist_msi (for making an installer)

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "Word Bomber",
        version = "1.2",
        options={"build_exe": {"packages":[],
                           "include_files":["assets"]}},
        description = "My first complete game!",
        executables = [Executable("Game.py", base=base)])