from log import *
lg.set_fn(__file__)
from ti_system import *
from ti_draw import *
from math import *
from format import *


class HTMLTokenizer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
    
    def next_token(self):
        if self.pos >= len(self.text):
            return None
        
        if self.text[self.pos] == "<":
            # Closing tag
            if self.text[self.pos:self.pos+2] == "</":
                end = self.text.find(">", self.pos)
                tag = self.text[self.pos+2:end]
                self.pos = end + 1
                return ("end_tag", tag.strip())
            # Opening/self-closing tag
            else:
                end = self.text.find(">", self.pos)
                tag_content = self.text[self.pos+1:end]
                self.pos = end + 1
                return ("start_tag", tag_content.strip())
        else:
            # Text node
            end = self.text.find("<", self.pos)
            if end == -1:
                end = len(self.text)
            text = self.text[self.pos:end]
            self.pos = end
            return ("text", text)

def parse(html):
    tokenizer = HTMLTokenizer(html)
    stack = [HTMLElement("html", "__document__")]
    
    while True:
        token = tokenizer.next_token()
        if token is None:
            break
        
        ttype, value = token
        
        if ttype == "start_tag":
            parts = value.split()
            tag = parts[0]
            attrs = {}  # TODO: parse attrs
            elem = HTMLElement(tag, id=f"{tag}_{len(stack)}")
            stack[-1].appendChild(elem)
            stack.append(elem)
        
        elif ttype == "end_tag":
            if stack and stack[-1].tag == value:
                stack.pop()
            else:
                raise HTMLParsingError(F("Unexpected closing tag </%v>", value))
        
        elif ttype == "text":
            if value.strip():
                text_node = HTMLElement("text", id=f"text_{len(stack)}", innerText=value)
                stack[-1].appendChild(text_node)
    
    return stack[0]


# handling indentation for __str__/__repr__ for DOM
# code not shown

# class for HTMLParsingError, not shown

# class for a 2d point, not shown

# some other code not shown (idlist, taglist, etc)

document = None
class HTMLElement:
    def __init__(s, tag="div", id="tmp", par=document, classname=None, chdr=None, innerText=None, style=None):
        s.par=par
        s.chdr=chdr if chdr is not None else []
        if id not in idlist:
            s.id = id
            idlist.append(id)
        else:
            while (id in idlist):
                id += "_"
            s.id = id
        s.innerText = innerText if innerText is not None else ""
        s.classname = classname if classname is not None else ""
        s.style = style if style is not None else ""
        s.tag = tag
        s.attributes = {
            "id": s.id,
            "class": s.classname,
            "style": s.style
        }
    def getElementById(s, id: str) -> HTMLElement | None:
        if s.id == id:
            return s
        for child in s.chdr:
            found = child.getELementById(id)
            if found is not None:
                return found
        return None
    def getElementsByClass(s, classname: str) -> list[HTMLElement | None]:
        elems = []
        if classname in s.classname.split(" "):
            elems.append(s)
        for child in s.chdr:
            elems.extend(child.getElementById(classname))
        return elems
    
    def __repr__(s):
        return "implemntation not shown"
    def appendChild(s, o):
        if type(o) == HTMLElement:
            s.chdr.append(o)
            o.par = s
        else:
            s.chdr.append(parse(o))
    def removeChild(s, o):
        s.chdr.remove(o)

document = HTMLElement("html", "__document__", None)
document.appendChild(HTMLElement("head", id="head"))
document.appendChild(HTMLElement("body", id="body"))

document.head = document.getElementById("head")
document.body = document.getElementById("body")
