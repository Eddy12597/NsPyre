import ti_system as tis
from log import *
# safely ignore the type warnings about the first argument not being 'self'.
lg.set_fn(__file__)

# currently useless
class _ios:
    def __init__(s, mode):
        s.mode = mode
    def __or__(s, o):
        return _ios(s.mode + " " + o.mode)
    def __contains__(s, o):
        return o.mode in s.mode

# models the mode for std::fstream in c++, but currently not very useful
ios_in = _ios("in")
ios_out = _ios("out")
ios_app = _ios("app")

# uses the ti system module's store_list and recall_list functions for persistent 'file' storage. Takes intuiton from the fact that a file is a collection of lines and each line, a str, is just a list[int] where the int is the ascii of the character
class file:
    def __init__(s, filename: str, mode: _ios = ios_in | ios_out | ios_app):
        s.filename = filename
        s.mode = mode
        s.m_in = ios_in in s.mode
        s.m_out = ios_out in s.mode
        s.m_app = ios_app in s.mode
        if not s.m_app:
            s.buffer = [] # list[int]
            lg.warn("not in append mode. emptying buffer")
            s.aved=False
        else:
            s.buffer = (s._load_content_to_buffer(s.filename))
            lg.info("buffer length: " + str(len(s.buffer)))
        if not s._check_fn():
            s.filename = "".join([(ch if ch.isdigit() or ch.isalpha() else "") for ch in s.filename])
            try:
                while(s.filename[0].isdigit()):
                    s.filename=s.filename[1:]
                lg.warn("filename sanitized to " + s.filename)
            except:
                lg.fatal("cannot sanitize file name, changed to 'null'")
                s.filename = "null"
    def writeline(s, text: str):
        for ch in text:
            s.buffer.append(ord(ch))
        s.buffer.append(10) # new line terminator
        s.saved = False
    def _parse_nlt_list(s, list_ords: list[int]):
        termidx=list_ords.index(10)
        if termidx != len(list_ords) - 1:
            lg.warn("chars found after null terminator in " + str(list_ords))
        result = ""
        for i in range(termidx):
            result += chr(list_ords[i])
        return result
    def _linetoords(s, line: str):
        res=[]
        for ch in line:
            res.append(ord(ch))
        return res
    def toStrList(s):
        res=[""]
        s.update_buffer()
        lg.info("buffer length: " + str(len(s.buffer)))
        if s.buffer is None or len(s.buffer) == 0: return res
        for ord_ in s.buffer:
            if ord_ == 10:
                res.append("")
                continue
            res[-1] += chr(ord_)
        return res
    def __repr__(s):
        return "\n".join(s.toStrList())
    def save(s, name: str | None = None):
        if name is None: name = s.filename
        tis.store_list(name, s.buffer)
        s.saved = True
    def _load_content_to_buffer(s, filename):
        try:
            s.buffer = tis.recall_list(filename)
            lg.info("file " + filename + " found. Buffer length: " + str(len(s.buffer)))
            s.saved = True
            return s.buffer
        except TypeError as te:
            lg.warn(repr(te)+" - file " + filename + " does not exist. emptying buffer...")
            s.buffer=[]
    def update_buffer(s):
        s._load_content_to_buffer(s.filename)
        s.saved=True
    def _check_fn(s, fn: str | None = None):
        if fn is None:
            fn = s.filename
        try:
            tis.store_list(fn, s.buffer)
            return True
        except:
            return False
    def edit(s, line: int, newcontent: str):
        flist = s.toStrList()
        flist[max(min(line, len(flist) - 1), 0)] = newcontent
        s.buffer = []
        for i in range(len(flist)):
            s.buffer.extend(s._linetoords(flist[i]))
            if i != len(flist) - 1:
                s.buffer.append(10)
        s.save()

    def insert(s, line: int, content: str):
        flist = s.toStrList()
        if line < 0:
            line = 0
        elif line > len(flist):
            line = len(flist)

        flist.insert(line, content)

        s.buffer = []
        for i, text_line in enumerate(flist):
            s.buffer.extend(s._linetoords(text_line))
            if i != len(flist) - 1:
                s.buffer.append(0)
        s.save()
