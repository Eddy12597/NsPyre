# format library for java-like substring and potential implementation of the printf function (since micropython 3.4 has no f strings, so every time either use str() + '+' or "".format()

def substr(s: str, a: int = -1, b: int = 10000000) -> str:
    res = ""
    s = str(s) # helpful for strict rounding in python

    st = max(0, a)
    end = min(b, len(s))
    for i in range(st, end):
        res += s[i]
    return res
