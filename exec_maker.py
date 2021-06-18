import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "Word Bomber",
        version = "1.0",
        options={"build_exe": {"packages":["pygame"],
                           "include_files":["assets"]}},
        description = "My first complete game!",
        executables = [Executable("wordbomber.py", base=base)])