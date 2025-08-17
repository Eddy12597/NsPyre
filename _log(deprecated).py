# Logging utility library for Python on TI Nspire

import ti_system as tis

logmsglist = []
logcallstack = []

indentlvl=0
indstr=""
_idx=0
_start_time=tis.get_time_ms()
_filename=__file__

def _lgfn(n):
    global _filename
    _filename = n

def _lg(m):
    global _idx
    try:
        logmsglist.append(str(_idx) + ": " + _filename.split("/")[_filename.count("/")][0:_filename.split("/")[_filename.count("/")].index(".py")] + ": " + str(tis.get_time_ms() - _start_time) + "ms: " + str(m))
        _idx += 1
    except:
        _lg("an error occurred in logging")

def _showlogs():
    idx=0
    while (idx < len(logmsglist)) and (input('-- More -- (q to quit)')) not in ["q", "Q", "exit", "esc"]:
        for i in range(idx, min(idx+11, len(logmsglist))):
            print(logmsglist[i])
        idx += 10
disabled = False
class lg:
    def disable():
        global disabled
        disabled=False
    def enable():
        global disabled
        disabled=True
    def set_fn(name):
        _lgfn(name)
    def raw(*args):
        if disabled:
            return
        for a in args:
            _lg(a)
    def call(fn_name: str, *args):
        if disabled: return
        global indstr, indentlvl
        logcallstack.append(fn_name)
        lg.cus("fn", indstr*indentlvl + "fn: "+fn_name+" ("+str(args)+")")
        indentlvl += 1
    def end(retval=None):
        if disabled: return
        global indstr, indentlvl
        if len(logcallstack) > 0:
            indentlvl -= 1
            lg.cus("fn", indstr*indentlvl + "end fn: "+logcallstack.pop() + "->"+str(retval))
        else:
            lg.warn("log call stack already empty")
    def stack():
        for s in logcallstack:
            print(str(s))
    def clearstack():
        logcallstack.clear()
    def show():
        # use 10 as font size
        print("=====+++++==           LOGS           ==+++++=====")
        _showlogs()
        print("=====+++++==    END OF LOGS    ==+++++=====")
    def info(*args):
        if disabled: return
        for a in args:
            _lg("[info] " + str(a))
    def warn(*args):
        if disabled: return
        for a in args:
            _lg("[warn] " + str(a))
    def fatal(*args):
        if disabled: return
        for a in args:
            _lg("[fatal] " + str(a))
    def cus(level: str, *args):
        if disabled: return
        for a in args:
            _lg("["+str(level)+"] "+str(a))
    # Doesn't work for now, good first issue/PR
    def level(lvl):
        level=str(lvl)
        lst=[]
        for m in logmsglist:
            tmp=""
            left=False
            rightidx=14
            for i in range(9, len(m)):
                if left:
                    if m[i] == "]":
                        rightidx = i + 1
                        break
                        tmp += m[i]
                    if m[i] == "[":
                        left=True
            if tmp == lvl:
                lst.append(m[rightidx+1:len(m)-1])
        return lst

# Ignore warnings if working in an IDE, this works, the lg class is static.
lg.info("logging set up")
lg.enable()

# tip: after the end of a buggy session, you can lg.show() in the shell, and press enter to incrementally show log messages.