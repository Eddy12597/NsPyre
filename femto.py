# femto - text editor
from log import *
import cli
import ti_draw as d
import fileio as fio
import time as t
lg.set_fn(__file__)

def _can_int(s: str):
    try:
        __a = int(s)
        return True
    except:
        return False

class femto:
    def __init__(s, name: str):
        s.cli = cli.cli() # renderer object
        s.file = fio.file(name, fio.ios_app | fio.ios_in | fio.ios_out) # persistent file storage
        s.name=name # file name
        s.cli.cls() # clear screen first
        s.running=False
        s.pgno=0 # page number
        s.nolpp=8 # number of lines per page
        s.curl=1 # current line number
    def start(s):
        s.running=True
        while s.running:
            d.use_buffer()
            flist=s.file.toStrList()
            s.cli.display("Femto - Text Editor")
            s.cli.display("File: " + s.file.filename + ("" if s.file.saved else "[*]"))
            s.cli.display("Currently on rel. line " + str(s.curl) + ", page="+str(s.pgno))
            s.cli.display("===============")
            for i in range(min(min(s.nolpp, len(flist)), len(flist)-s.nolpp*s.pgno)):
                s.cli.display(str(i+1)+"/"+str(s.pgno*s.nolpp+s.curl)+": "+flist[s.pgno+i])
            s.cli.display("===============")
            s.cli.display("Enter command: ")
            cmd=s.cli.getInut(":")
            lg.info("cmd="+cmd)
            if cmd == "q": # quit
                s.running=False
            elif cmd == "e": # edit
                s.cli.display("Enter new content:")
                nc=s.cli.getInput(":")
                s.file.edit(s.pgno*s.nolpp+s.curl-1, nc)
                flist = s.file.toStrList()
                s.file.saved=False
            elif cmd=="s": # save
                s.file.save()
                s.cli.display("Saved to " + s.name)
                s.file.saved=True
            elif cmd == "n": # next page
                s.pgno += (1 if s.pgno * s.nolpp + s.curl < len(flist) - 1 else 0)
            elif cmd == "p": # previous page
                s.pgno -= (1 if s.pgno * s.nolpp + s.curl > 0 else 0)
            elif cmd == "a": # add a line
                s.file.insert(s.pgno * s.nolpp + s.curl, "")
                s.file.saved = False
            elif _can_int(cmd): # go to line number
                ln = int(cmd)
                if ln < 0 or ln > s.nolpp:
                    s.cli.display("line out of range")
                elif ln == 0:
                    ln = 1
                s.curl = ln
            
            d.paint_buffer()
            t.sleep(0.04)
            s.cli.cls()
        lg.info("user quit femto")
f=None

def test():
    global f
    f=femto("hello")
    lg.info("file hello created, mode=app")
    f.file.writeline("wtf")
    f.file.writeline("line 2")
    f.file.writeline("line 3")
    f.file.writeline("a longer line blah blah blah")
    f.file.writeline("another line")
    f.file.writeline("and another")
    f.file.writeline("blah blah blah")
    f.file.writeline("wow LOL")

    f.file.save()
    lg.info("saved. femto starting:")
    f.start()

def main():
    try:
        test()
    except BaseException as e:
        lg.fatal(repr(e))
        f.cli.cls()
        f.cli.color=(255, 0,0)
        f.cli.display("an error occurred. check logs for more info")
