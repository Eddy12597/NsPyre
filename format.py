# format library for java-like substring and potential implementation of the printf function (since micropython 3.4 has no f strings, so every time either use str() + '+' or "".format()

def substr(s: str, a: int = -1, b: int = 10000000) -> str:
    res = ""
    s = str(s) # helpful for strict rounding in python

    st = max(0, a)
    end = min(b, len(s))
    for i in range(st, end):
        res += s[i]
    return res


# can be used with print(f(...)), providing a modern pythonic printf option.
def f(fmt, *args):
    i = 0
    res=""
    args = list(args)
    while i < len(fmt):
        if fmt[i] == '\\':
            if i + 1 < len(fmt):
                esc = fmt[i+1]
                if esc == 'n':
                    res += "\n"
                elif esc == 't':
                    res += '\t'
                elif esc == '\\':
                    res += '\\'
                i += 2
            else:
                i += 1
        elif fmt[i] == '%' and i + 1 < len(fmt) and fmt[i+1] == 'v':
            if args:
                res += str(args.pop(0))
                i += 2
        else:
            res += fmt[i]
            i += 1
    return res
