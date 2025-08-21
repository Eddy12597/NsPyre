# Stock Simulator with Buy/Sell and, in the future, algorithmic trading (primitive)

import ti_system as tis
# remove this next line when copying to calculator:
import numpy as np
# delete the next 3 lines
def _randn(x):
    return np.random.randn();
tis._variable_store.update({"randn", _randn})

from random import *
from math import *
import ti_plotlib as plt
import ti_draw as d
from cmath import *
from time import *


wait_time = 0.1

print("B to buy, S to short, C to close, A for algorithmic trading")
sleep(1)
sgn = ""
maxh = 250

# did bot close buy/short position?
botcloseb = False
botclosesh = False 

pos = 0 # 1 = long, 0 = close, -1 = short

def disptxt (x: int | float, y: int | float, c: str | tuple[int, int, int], txt: str) -> None:
    d.clear_rect(x, y, 20, len(c) * 50 + 20)
    if c == "r":
        c = (228, 8, 10)
    elif c == "g":
        c = (180, 200, 60)
    elif c == "b": # i was stupid, didnt realize this is ambiguous but whatever
        c = (0, 0, 0)
    elif c == "y":
        c = (200, 200, 50)
    d.set_color(c)
    d.draw_text(x, y, txt)
    d.set_color(200, 200, 50)

def mx(a, b):
    if a > b:
        return a
    return b

def mn(a, b):
    if a > b:
        return b
    return a

def pltcandle(xpos, w, o, h, l, c) -> None:
    if c > 0:
        # bullish
        d.set_color(60, 200, 180)
        d.draw_rect(xpos - w / 2, o, w, c-o)
        d.draw_line(xpos, o, xpos, l)
        d.draw_line(xpos, c, xpos, h)
    else:
        # bearish
        d.set_color(228, 8, 10)
        d.fill_rect(xpos - w/2, c, w, o-c)
        d.draw_line(xpos, c, xpos, l)
        d.draw_line(xpos, o,xpos, h)

def randnorm(m=0, std=1):
    return tis.eval_function("randn", 0)* std + m # here 0 is just a placeholder, ti_system specified that it must be a one-argument function