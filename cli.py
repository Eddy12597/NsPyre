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
    def __init__(s, clisets: dict | None = None, guisets: dict | None = None): # includes cli and gui settings

        # Needs refactoring (using dict.get)
        # cli settings
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

        # gui settings
        try: s.color = guisets["color"]
        except: s.color = (250, 250, 250)
        try: s.background_color = guisets["background_color"]
        except: s.background_color = (40, 40, 45)
        try: s.cursor = guisets["cursor"]
        except: s.cursor = "|"
        try: s.prompt_end_char = guisets["prompt_end_char"]
        except: s.prompt_end_char = "$"
        try: s.arrow_list = guisets["arrow_list"]
        except: s.arrow_list = {
            "up": "^", # this works in ti nspire
            "down": "exp",
            "left": "left", # left arrow
            "right": "right",
        }
            
        d.set_window(0, 318, 0, 18)
        d.set_color(s.background_color)
        d.fill_rect(0, 0, 318, 18)
        d.set_color(s.color)
    
    def getPrefix(s):
        return s.user_name + ":" + str(s.cwd) + s.prompt_end_char + " "
    def setLastLine(s, text: str) -> None:
        # lg.call("setLastLine", text)
        s.text_history[-1] = text
        # lg.end("setLastLine")
    
    def setCwd(s, newCwd: fs.folder): # the `cd` command
        s.cwd = newCwd
    def clearscreen(s):
        d.set_color(s.background_color)
        d.fill_rect(0, 0, 318, 18) # can't change font size on calculator, so 18 lines would fit when the font size is 10 units (in python editor, menu->1->6)
        d.set_color(s.color)
    def display(s, text: str | None = None):
        if text is not None:
            s.text_history.append(text)
        if len(s.text_history) > 18: # only draw latest 18 (with relation to s.scrollup)
            s.clearscreen()
            for i in range(1, 19):
                d.draw_text(0, 18-i, str(s.text_history[-(18-i) - 1 - s.scrollup]))
                # overflow-x
                if len(s.text_history[-1]) > 50:
                    s.display(s.text_history[-1][51:])
            d.paint_buffer()
        else:
            s.clearscreen()
            d.use_buffer()
            for i in range(1, len(s.text_history) + 1):
                d.draw_text(0, 18-i, s.text_history[i-1])
            d.paint_buffer()
    # future:
    """
    def blinkCursor(s, numsPerSec: int = 1.5, minlen=0):
        # blinks the cursor at a given frequency.
        # returns any key that is pressed (apart from del and the arrow keys) -> used
        # in other functions like getInput
        # will be integrated into the getInput function
    """

    def getInput(s, prompt: str) -> str:
        lg.call("getInput", prompt)
        s.display(prompt)
        result = ""
        while True:
            k = tis.get_key()
            if k == "esc":
                break
            if k == "enter":
                return result
            if k != "":
                if not (k.startswith("del")) and not (k in s.arrow_list.values()):
                    s.setLastLine(
                        # from format.py, cleaner syntax than [::]
                        # signature: (string: str, start: int, end: int)
                        # start is inclusive, end is exclusive
                        substr(
                            s.text_history[-1], 
                            0, 
                            len(s.text_history[-1]) - s.cursorleft - 0 # kept here, try toggling if buggy
                        ) + k + substr(
                            s.text_history[-1],
                            len(s.text_history[-1]) - s.cursorleft,
                            len(s.text_history[-1])           
                        )
                    )
                elif k.startswith("del"):
                    if len(s.text_history[-1]) > len(prompt):
                        s.text_history[-1] = substr(
                            s.text_history[-1],
                            0, len(s.text_history[-1]) - s.cursorleft - 1
                        ) + substr(
                            s.text_history[-1],
                            len(s.text_history[-1]) - s.cursorleft, len(s.text_history[-1])
                        )
                elif k in s.arrow_list.values():
                    if k == s.arrow_list["up"]:
                        lg.info("up key")
                        s.scrollup += 1 if s.scrollup < len(s.text_history) - 18 else 0
                    elif k == s.arrow_list["down"]:
                        lg.info("down key")
                        s.scrollup -= 1 if s.scrollup > 0 else 0
                    elif k == s.arrow_list["left"]:
                        lg.info("left key")
                        s.cursorleft += (1 if s.cursorleft < len(s.text_history[-1]) - len(prompt) else 0)
                    elif k == s.arrow_list["right"]:
                        lg.info("right key")
                        s.cursorleft -= 1 if s.cursorleft > 0 else 0

                # end of checking key type (normal, del, arrow)
                s.display()
                # try patch: clear screen?
                # t.sleep(0.01)
                # s.clearscreen()
                # Doesn't work
            # end of checking whether key pressed is empty or not
            result = s.text_history[-1][len(prompt):len(s.text_history[-1])]
            t.sleep(0.01)
        # end of while loop
        lg.end(result)
        return result
    # windows `cls` and unix `clear`
    def cls(s, prompt = ""):
        s.text_history = []
        s.clearscreen()
        s.display(prompt)
    