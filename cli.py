# object oriented approach to screen rendering

from log import *
lg.set_fn(__file__)

import math as m
import ti_draw as d
import ti_system as tis
import time as t
import filesys as fs
from format import *

def clamp(_min, x, _max):
    return min(_max, max(_min, x))

class cli:
    def __init__(s, clisets: dict = None, guisets: dict = None): # includes cli and gui settings
        s.scrollup = 0 # cursor upward scroll
        s.cursorleft = 0 # position of cursor with relation to EOL
        s.root = fs.root # link file system to cli for easier integration with terminal.py
        try: s.user_name = clisets["user_name"]
        except: s.user_name = "root"
        try: s.passwd = clisets["passwd"]
        except: s.passwd = "1234"
        try: s.text_history = clisets["text_history"] # keeping track of history. text_history[-1] is used very often for last line manipulation. Other programs using the cli api could manipulate text_history for multi-line input handling with custom cursor vertical position control and detection, but that could be integrated to cli.py for efficiency i guess
        except: s.text_history = []
        try: s.cwd = clisets["cwd"] # current working directory
        except: s.cwd=s.root # s.cwd: folder
